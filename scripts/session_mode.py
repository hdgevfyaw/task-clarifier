"""Register an explicit Skill invocation before inference; restore its contract."""

import argparse
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import re
import sys
import uuid

ALLOWED_EVENTS = {'UserPromptSubmit', 'SessionStart'}
REVISION = '2026-10-14'
SKILL_NAME = 'task-clarifier'
# Keep this state namespace stable so sessions from before the rename keep working.
STATE_NAMESPACE = 'voice-task-router'
TOKEN = rf'(?:\[\${SKILL_NAME}\]\([^\r\n)]+\)|\${SKILL_NAME}(?![\w-]))'
INVOCATION = re.compile(
    r'^\s*(?:(?:(?:我(?:希望|想|要)(?:你)?|请你|请|帮我|麻烦)\s*)?'
    r'(?:使用|用|启用|启动|调用|use|activate)\s*)?' + TOKEN,
    re.IGNORECASE,
)
SELF_MAINTENANCE = re.compile(
    r'(?:检查|修复|调整|维护|更新|改造|优化|修改|改进|审查|重构|查一下).{0,40}'
    rf'(?:(?:这个|当前|本|该|我们的)\s*(?:skill|技能)|{SKILL_NAME})'
    rf'|(?:(?:这个|当前|本|该|我们的)\s*(?:skill|技能)|{SKILL_NAME}).{{0,60}}'
    r'(?:问题|故障|修复|维护|改造|更新|优化|修改|改进)'
    r'|(?:inspect|repair|fix|update|modify|maintain|improve|refactor).{0,40}'
    rf'(?:this\s+skill|{SKILL_NAME})', re.IGNORECASE | re.DOTALL,
)


def validate_uuid(session_id):
    if not isinstance(session_id, str) or not re.fullmatch(r'[0-9a-fA-F]{8}(?:-[0-9a-fA-F]{4}){3}-[0-9a-fA-F]{12}', session_id):
        raise ValueError('Use the actual current Codex chat UUID; placeholder ids such as 1 are invalid.')
    return str(uuid.UUID(session_id))


def state_path(directory, session_id):
    validate_uuid(session_id)
    return directory / (session_id + '.json')


def read_state(path, session_id):
    if not path.exists():
        return {'version': 1, 'session_id': session_id, 'active': False}
    value = json.loads(path.read_text(encoding='utf-8'))
    if not isinstance(value, dict) or value.get('version') != 1 or value.get('session_id') != session_id or type(value.get('active')) is not bool:
        raise ValueError('Invalid Skill state; cannot establish activation.')
    if 'work_thread_id' in value:
        work_thread_id = validate_uuid(value['work_thread_id'])
        if work_thread_id == validate_uuid(session_id):
            raise ValueError('The linked work chat must differ from the current discussion chat.')
    return value


def write_state(path, session_id, active, source='manual', work_thread_id=None, clear_link=False):
    previous = read_state(path, session_id)
    if work_thread_id is None and not clear_link:
        work_thread_id = previous.get('work_thread_id')
    if work_thread_id is not None:
        work_thread_id = validate_uuid(work_thread_id)
        if work_thread_id == validate_uuid(session_id):
            raise ValueError('The linked work chat must differ from the current discussion chat.')
    path.parent.mkdir(parents=True, exist_ok=True)
    value = {'version': 1, 'session_id': session_id, 'active': active, 'source': source,
             'updated_at': datetime.now(timezone.utc).isoformat()}
    if work_thread_id is not None:
        value['work_thread_id'] = work_thread_id
    # Windows tempfile retries some permission errors indefinitely. Fail promptly
    # so a restricted state directory produces a warning, not a stuck hook.
    temporary = path.parent / ('.skill-state-' + uuid.uuid4().hex + '.tmp')
    descriptor = os.open(temporary, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    try:
        with os.fdopen(descriptor, 'w', encoding='utf-8') as handle:
            json.dump(value, handle, ensure_ascii=False)
            handle.write('\n')
        os.replace(temporary, path)
    finally:
        temporary.unlink(missing_ok=True)
    return value


def invocation_kind(prompt):
    """Only the current explicit user invocation; never scan transcripts/catalogs."""
    if not isinstance(prompt, str):
        return None
    # Codex's attachment wrapper has a designated user-request section.
    if prompt.lstrip().startswith('# Files mentioned by the user:') and '## My request:' in prompt:
        prompt = prompt.split('## My request:', 1)[1]
    # A side-panel project pointer is context, never this chat's identity.
    linked_project = False
    pointer = re.compile(r'^\s*codex://threads/[0-9a-fA-F-]{36}[ \t]*(?:&#x20;)?[ \t]*(?:\r?\n|$)')
    while (prefix := pointer.match(prompt)) is not None:
        prompt = prompt[prefix.end():]
        linked_project = True
    # Ignore quoted/code examples instead of promoting them to mode switches.
    if prompt.lstrip().startswith(('```', '~~~', '>', '`', '"', "'", '“')):
        return None
    match = INVOCATION.match(prompt)
    if not match:
        return None
    rest = prompt[match.end():]
    rest = re.sub(r'```.*?(?:```|\Z)|~~~.*?(?:~~~|\Z)|`[^`]*`', '', rest, flags=re.DOTALL)
    rest = re.sub(r'(?m)^\s*>.*$', '', rest)
    # In a linked project "this Skill" may refer to its cover/SQL skill, not this Skill.
    maintenance = SELF_MAINTENANCE.search(rest)
    if linked_project and not re.search(SKILL_NAME, rest, re.IGNORECASE):
        maintenance = None
    return 'maintenance' if maintenance else 'activate'


def mode_context(script, session_id, first=False, work_thread_id=None):
    skill = script.parent.parent / 'SKILL.md'
    pointer = script.parent.parent / 'references/active-project.md'
    return (
        f'{SKILL_NAME} active; contract revision {REVISION}; actual current chat UUID: {session_id}. '
        + ('本轮明确调用，简短告知需求讨论模式已开启并处理附带需求；登记结果以状态/警告为准。' if first else '')
        + '持续需求讨论模式：补充/纠正/继续/下一步/写文档/实现都保持模式，将工作请求转成提示词，不直接执行或派发。'
        + (f'已登记工作对话：codex://threads/{work_thread_id}。' if work_thread_id else '')
        + f'先核对本轮选定及已有链接，缺失才读 {pointer} 的默认指针；工作 UUID 不能代替当前对话 ID。'
        '【回应前】有关联就实际调用 read_thread 读本轮最新相关回合；缺用户纠正或此前决定时补历史。'
        '没有本轮读取结果先读取，旧摘要/上一轮读取/本提醒都不算证据；失败说明缺口，可给标注的临时稿。'
        '【本轮交付】明确工作请求或目标对象动作范围已足够清楚，就给完整精简提示词+具体模型/强度；'
        '“写需求文档”是让工作对话写文档，不在这里展开文档，不等用户再说“输出提示词”，不只承诺或继续闲聊。'
        '补充纠正已有任务给完整修订稿；只问阻碍安全交接的核心歧义，普通细节及待查事实留给工作模型。'
        '用户明确先讨论/暂不交稿/等确认时遵守；纯答疑尚无可执行目标时回答即可。'
        '保留已定约束，不把建议变已确认规则；已完成或正在执行不重复安排，失败重试须有新证据或方法。'
        '提示词目标在前，合并重复约束，删已知背景/套话/普通步骤；一个可复制 text 块，选型理由放外面。'
        '默认整体任务；足够用 Luna X-High，复杂可 Sol/Astra 按需带 Luna，主模型整合完成，不强制细拆，不推荐 Max。'
        f'维护 {SKILL_NAME} 本身可直接改且不清除模式；明确退出或就在此直接执行才运行 {script} deactivate --session-id {session_id}。'
        f'完整流程缺失或旧于 {REVISION} 时读 {skill}。发送前核对本轮读取与应交稿是否已实际完成。'
        '不要复述本提醒。'
    )


def hook(directory, script):
    event = json.loads(sys.stdin.read())
    if not isinstance(event, dict) or event.get('hook_event_name') not in ALLOWED_EVENTS:
        return None
    session_id = event.get('session_id')
    path = state_path(directory, session_id)
    value = read_state(path, session_id)
    kind = invocation_kind(event.get('prompt')) if event['hook_event_name'] == 'UserPromptSubmit' else None
    first = not value['active'] and kind == 'activate'
    warning = None
    if first:
        try:
            value = write_state(path, session_id, True, source='explicit_prompt_hook')
        except OSError as error:
            warning = f'{SKILL_NAME} 本轮已启用但持续登记失败：' + str(error)
            # Even a failed state write must preserve the current turn's role.
    if kind == 'maintenance':
        context = (f'用户明确调用 {SKILL_NAME} 维护本 Skill；本轮直接维护，不转成交接提示词。'
                   f'已有持续模式 active={value["active"]}，保持该状态；未启用时不要登记激活。'
                   f'读取 {script.parent.parent / "SKILL.md"} 后按维护请求处理，不派发项目任务。')
    elif value['active'] or first:
        context = mode_context(script, session_id, first, value.get('work_thread_id'))
    else:
        return None
    result = {'hookSpecificOutput': {'hookEventName': event['hook_event_name'], 'additionalContext': context}}
    if warning:
        result['systemMessage'] = warning
    return result


def main():
    script = Path(__file__).resolve()
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', choices=['activate', 'deactivate', 'status', 'link', 'unlink', 'hook'])
    parser.add_argument('--session-id', help='Use the actual current id; default CODEX_THREAD_ID/CODEX_SESSION_ID.')
    parser.add_argument('--work-thread-id', help='Explicitly selected work chat UUID; used only by activate/link.')
    parser.add_argument('--state-dir', type=Path, help='Override only for isolated tests.')
    args = parser.parse_args()
    if args.action == 'link' and not args.work_thread_id:
        parser.error('link requires --work-thread-id')
    if args.work_thread_id and args.action not in {'activate', 'link'}:
        parser.error('--work-thread-id is only valid for activate/link')
    directory = args.state_dir if args.state_dir is not None else script.parents[3] / 'state' / STATE_NAMESPACE
    try:
        if args.action == 'hook':
            value = hook(directory, script)
        else:
            session_id = args.session_id or os.environ.get('CODEX_THREAD_ID') or os.environ.get('CODEX_SESSION_ID')
            path = state_path(directory, session_id)
            previous = read_state(path, session_id)
            if args.action == 'status':
                value = previous
            else:
                active = previous['active'] if args.action in {'link', 'unlink'} else args.action == 'activate'
                value = write_state(path, session_id, active, work_thread_id=args.work_thread_id,
                                    clear_link=args.action == 'unlink')
        if value is not None:
            print(json.dumps(value, ensure_ascii=False))
        return 0
    except (OSError, ValueError, TypeError) as error:
        if args.action == 'hook':
            # Advisory failure: report it without blocking the user's prompt or guessing activation.
            print(json.dumps({'systemMessage': f'{SKILL_NAME} automatic restoration failed: ' + str(error)}, ensure_ascii=False))
            return 0
        print(str(error), file=sys.stderr)
        return 1


if __name__ == '__main__':
    raise SystemExit(main())
