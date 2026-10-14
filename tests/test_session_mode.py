"""Exercise real hook events and CLI state transitions in isolated directories."""

import importlib.util
import io
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch


SCRIPT = Path(__file__).resolve().parents[1] / 'scripts' / 'session_mode.py'
spec = importlib.util.spec_from_file_location('session_mode', SCRIPT)
mode = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mode)

CHAT = '11111111-1111-4111-8111-111111111111'
WORK = '22222222-2222-4222-8222-222222222222'
OTHER = '33333333-3333-4333-8333-333333333333'


class SessionModeTests(unittest.TestCase):
    def setUp(self):
        # Stay in the writable checkout rather than a sandbox's restricted OS temp.
        self.temp = tempfile.TemporaryDirectory(prefix='.task-clarifier-test-', dir=SCRIPT.parents[1])
        self.directory = Path(self.temp.name)
        self.assertEqual(self.directory.resolve().parent, SCRIPT.parents[1].resolve())
        self.addCleanup(self.temp.cleanup)
        self.path = mode.state_path(self.directory, CHAT)

    def event(self, prompt=None, event='UserPromptSubmit', chat=CHAT, **extra):
        value = {'hook_event_name': event, 'session_id': chat, **extra}
        if prompt is not None:
            value['prompt'] = prompt
        with patch.object(sys, 'stdin', io.StringIO(json.dumps(value))):
            return mode.hook(self.directory, SCRIPT)

    def cli(self, action, *extra):
        return subprocess.run(
            [sys.executable, '-X', 'utf8', str(SCRIPT), action,
             '--state-dir', str(self.directory), '--session-id', CHAT, *extra],
            capture_output=True, text=True, encoding='utf-8',
        )

    def test_explicit_invocation_registers_actual_event_chat(self):
        output = self.event(f'codex://threads/{WORK}\n$task-clarifier 写需求文档')
        self.assertTrue(mode.read_state(self.path, CHAT)['active'])
        self.assertFalse(mode.state_path(self.directory, WORK).exists())
        self.assertEqual(output['hookSpecificOutput']['hookEventName'], 'UserPromptSubmit')

    def test_markdown_skill_invocation_registers(self):
        self.event('[$task-clarifier](C:/skills/task-clarifier/SKILL.md) 理清需求')
        self.assertTrue(mode.read_state(self.path, CHAT)['active'])

    def test_followups_keep_state_and_receive_context_without_reinvocation(self):
        self.event('$task-clarifier 理清存档管理需求')
        original = self.path.read_bytes()
        for prompt in ('这个功能解决什么问题？', '自动和手动同等管理',
                       '纠正：管理页不读取进度', '写完整需求文档',
                       '继续', '按这个改', '先别出提示词，先讨论方案'):
            with self.subTest(prompt=prompt):
                output = self.event(prompt)
                self.assertIsNotNone(output)
                self.assertIn(CHAT, output['hookSpecificOutput']['additionalContext'])
                self.assertEqual(self.path.read_bytes(), original)

    def test_start_resume_and_compaction_restore_saved_association(self):
        mode.write_state(self.path, CHAT, True, work_thread_id=WORK)
        original = self.path.read_bytes()
        for source in ('startup', 'resume', 'compact', 'clear'):
            with self.subTest(source=source):
                output = self.event(event='SessionStart', source=source)
                self.assertIn(f'codex://threads/{WORK}', output['hookSpecificOutput']['additionalContext'])
                self.assertEqual(self.path.read_bytes(), original)

    def test_other_chats_do_not_inherit_mode(self):
        mode.write_state(self.path, CHAT, True, work_thread_id=WORK)
        self.assertIsNone(self.event('继续', chat=OTHER))
        self.assertFalse(mode.state_path(self.directory, OTHER).exists())

    def test_inactive_generic_task_does_not_force_activation(self):
        self.assertIsNone(self.event('帮我写需求文档'))
        self.assertFalse(self.path.exists())

    def test_quoted_tokens_and_attachment_content_do_not_activate(self):
        for prompt in ('> $task-clarifier', '```text\n$task-clarifier\n```',
                       '这是调用示例：$task-clarifier',
                       '# Files mentioned by the user:\n$task-clarifier\n## My request:\n解释截图'):
            with self.subTest(prompt=prompt):
                self.assertIsNone(self.event(prompt))
                self.assertFalse(self.path.exists())

    def test_attachment_user_request_can_activate(self):
        self.event('# Files mentioned by the user:\nfile.png\n## My request:\n$task-clarifier 写需求文档')
        self.assertTrue(mode.read_state(self.path, CHAT)['active'])

    def test_maintenance_does_not_activate_inactive_chat(self):
        self.assertIsNotNone(self.event('$task-clarifier 优化这个skill'))
        self.assertFalse(self.path.exists())

    def test_maintenance_keeps_existing_mode_and_link(self):
        mode.write_state(self.path, CHAT, True, work_thread_id=WORK)
        original = self.path.read_bytes()
        self.assertIsNotNone(self.event('$task-clarifier 修改这个skill'))
        self.assertEqual(self.path.read_bytes(), original)
        output = self.event('继续')
        self.assertIn(f'codex://threads/{WORK}', output['hookSpecificOutput']['additionalContext'])

    def test_legacy_state_without_link_restores(self):
        self.path.write_text(json.dumps({'version': 1, 'session_id': CHAT, 'active': True}), encoding='utf-8')
        self.assertIsNotNone(self.event('继续'))
        self.assertTrue(mode.read_state(self.path, CHAT)['active'])

    def test_cli_link_unlink_and_activation_preserve_independent_state(self):
        linked = self.cli('link', '--work-thread-id', WORK)
        self.assertEqual(linked.returncode, 0, linked.stderr)
        self.assertFalse(json.loads(linked.stdout)['active'])
        self.assertIsNone(self.event('继续'))
        activated = self.cli('activate')
        self.assertEqual(activated.returncode, 0, activated.stderr)
        self.assertEqual(json.loads(activated.stdout)['work_thread_id'], WORK)
        replaced = self.cli('link', '--work-thread-id', OTHER)
        self.assertTrue(json.loads(replaced.stdout)['active'])
        self.assertEqual(json.loads(replaced.stdout)['work_thread_id'], OTHER)
        unlinked = self.cli('unlink')
        self.assertTrue(json.loads(unlinked.stdout)['active'])
        self.assertNotIn('work_thread_id', json.loads(unlinked.stdout))
        mode.write_state(self.path, CHAT, True, work_thread_id=WORK)
        deactivated = self.cli('deactivate')
        self.assertFalse(json.loads(deactivated.stdout)['active'])
        self.assertEqual(json.loads(deactivated.stdout)['work_thread_id'], WORK)
        self.assertIsNone(self.event('继续'))
        restored = self.cli('activate')
        self.assertTrue(json.loads(restored.stdout)['active'])
        self.assertEqual(json.loads(restored.stdout)['work_thread_id'], WORK)

    def test_invalid_link_does_not_change_existing_state(self):
        mode.write_state(self.path, CHAT, True, work_thread_id=WORK)
        original = self.path.read_bytes()
        for work in (CHAT, CHAT.upper(), '1', '../outside', 'codex://threads/' + WORK):
            with self.subTest(work=work):
                output = self.cli('link', '--work-thread-id', work)
                self.assertNotEqual(output.returncode, 0)
                self.assertEqual(self.path.read_bytes(), original)

    def test_cli_rejects_missing_or_misplaced_link_argument(self):
        self.assertNotEqual(self.cli('link').returncode, 0)
        self.assertNotEqual(self.cli('status', '--work-thread-id', WORK).returncode, 0)
        self.assertFalse(self.path.exists())

    def test_invalid_current_ids_never_write_state(self):
        for chat in ('1', '../outside', WORK + '/extra', None):
            with self.subTest(chat=chat):
                with self.assertRaises(ValueError):
                    self.event('$task-clarifier', chat=chat)
        self.assertEqual(list(self.directory.iterdir()), [])

    def test_corrupt_state_cannot_silently_activate_or_overwrite(self):
        for value in ({'version': 1, 'session_id': OTHER, 'active': True},
                      {'version': 1, 'session_id': CHAT, 'active': 'true'},
                      {'version': 1, 'session_id': CHAT, 'active': True, 'work_thread_id': '1'},
                      {'version': 1, 'session_id': CHAT, 'active': True, 'work_thread_id': CHAT}):
            with self.subTest(value=value):
                original = json.dumps(value)
                self.path.write_text(original, encoding='utf-8')
                with self.assertRaises(ValueError):
                    self.event('$task-clarifier')
                self.assertEqual(self.path.read_text(encoding='utf-8'), original)

    def test_failed_registration_still_supplies_current_turn_context(self):
        with patch.object(mode, 'write_state', side_effect=OSError('read-only state directory')):
            output = self.event('$task-clarifier 写需求文档')
        self.assertIn('systemMessage', output)
        self.assertIn(CHAT, output['hookSpecificOutput']['additionalContext'])
        self.assertFalse(self.path.exists())

    def test_permission_failure_in_atomic_writer_returns_hook_warning(self):
        with patch.object(mode.os, 'open', side_effect=PermissionError('restricted directory')) as opened:
            output = self.event('$task-clarifier 写需求文档')
        self.assertEqual(opened.call_count, 1)
        self.assertIn('systemMessage', output)
        self.assertIn(CHAT, output['hookSpecificOutput']['additionalContext'])
        self.assertEqual(list(self.directory.iterdir()), [])

    def test_failed_atomic_replace_preserves_state_and_removes_temp_file(self):
        mode.write_state(self.path, CHAT, True, work_thread_id=WORK)
        original = self.path.read_bytes()
        with patch.object(mode.os, 'replace', side_effect=OSError('replace failed')):
            with self.assertRaises(OSError):
                mode.write_state(self.path, CHAT, False)
        self.assertEqual(self.path.read_bytes(), original)
        self.assertEqual(list(self.directory.iterdir()), [self.path])

    def test_unsupported_events_have_no_effect(self):
        self.assertIsNone(self.event('$task-clarifier', event='PreToolUse'))
        self.assertFalse(self.path.exists())


if __name__ == '__main__':
    unittest.main()
