# Task Clarifier

> **先把需求理清，再选择合适的模型与执行方式。**

Task Clarifier 是一个面向 Codex 的需求澄清与模型选择 Skill：把还没理顺的语音或文字想法，通过持续讨论整理成一份**清楚、精简、可直接交给工作对话执行的提示词**，并按任务难度建议模型、推理强度和必要的协作方式。

你不必一开始就会写提示词，也不用把要求一次讲完。先说个大概，想到新条件时继续补充，发现理解错了就纠正。Skill 会维护同一份需求草稿，只追问影响核心目标和范围的问题；明确提出工作任务或需求足够清楚时，本轮就给精简提示词和模型、推理强度建议，无需再说“输出提示词”。

## 本次更新｜2026-10-14

- 明确工作请求、可交接的需求及已有任务的补充纠正，本轮主动交提示词，减少连续讨论却迟迟不交稿；“先讨论、暂不交稿、确认后再写”的边界优先。
- “写完整需求文档”等请求生成让工作对话执行的提示词；只追问核心目标或范围歧义，普通细节和待查事实交工作模型处理，未定规则不擅自补成要求。
- 持续模式每轮提醒先取得关联工作对话的实际读取结果，缺相关决定或纠正时补历史；读取失败说明缺口，可以交标注的临时稿。
- 支持按讨论对话保存工作对话 UUID，恢复时注入正确关联；保留更名前的状态兼容，维护本 Skill 不开启或清除已有模式。更名后的 Hook 命令须指向新脚本路径。
- 提示词交稿前合并重复要求、删已知背景和套话，保留关键约束；继续推荐具体模型与强度，复杂任务仍可由主模型按需统筹 Luna。
- 新增隔离状态与 Hook 事件回归测试，覆盖连续跟进、启动与压缩恢复、关联替换、旧状态、退出及登记失败。脚本测试不代表真实模型行为已获保证。
- 修正受限 Windows 目录中的状态写入可能长时间重试的问题；无权限时及时报出登记失败，继续处理本轮需求。

## Latest update — 2026-10-14

- Deliver a prompt in the current turn for explicit work requests, sufficiently clear tasks, and task corrections; honor requests to discuss first or wait for confirmation.
- Treat “write a requirements document” as a handoff to the work chat. Leave ordinary implementation details and research questions to that model without inventing confirmed requirements.
- Require actual current-turn linked-chat reads before replying; fetch relevant history when needed and disclose read failures in provisional drafts.
- Persist an optional work-chat UUID per discussion chat and restore it with the mode. Keep legacy state compatible; renamed installations need hook commands pointing to the new script path.
- Trim repeated context and boilerplate while preserving constraints, concrete model/effort recommendations, and optional host-led Luna collaboration.
- Add isolated hook/state regression tests. Passing script tests does not guarantee real model compliance.
- Fail promptly on restricted Windows state writes instead of retrying until the hook times out.

## 30 秒看懂它怎么帮你

~~~mermaid
flowchart LR
    A["你自然地说出想法<br/>语音或文字都可以"] --> B["整理成一份持续更新的需求"]
    B --> C{"缺少会改变方案的关键信息吗？"}
    C -- "有：只问关键问题" --> D["你补充、纠正或调整方向"]
    D --> B
    C -- "没有：需求已清楚" --> E["完整执行提示词<br/>＋模型与推理强度建议"]
    E --> F["你复制到工作对话"]
    F -. "想到新要求 / 说下一步" .-> B
~~~

你负责表达和决定，Task Clarifier 负责理清需求、准备执行提示词并推荐合适的模型。它让需求在多轮讨论中保持连贯，但默认不会替你开始写代码、改项目、生成素材或把任务派给别人。

## 它解决什么麻烦？

好点子往往不是一份完整需求文档，而是一段口述，之后才慢慢补出限制、优先级和例子。普通的一问一答容易让信息散落在聊天里：改了一处却丢了旧约束，需求还没讲清就开始执行，或者最后仍要自己把几轮内容重新拼成提示词。

Task Clarifier 把这个过程变成一份持续维护的需求草稿：

| 常见情况 | 这个 Skill 怎么帮你 |
|---|---|
| 想法多，表达顺序比较乱 | 归纳目标、约束、例子和未知项，尽量保留原意 |
| 说完后又想起要求 | 把新信息并入同一份草稿，不必从头重讲 |
| 发现方向理解错了 | 更新有误的部分，同时保留仍适用的要求 |
| 不确定还要回答多少问题 | 只追问会改变方案的关键缺口，普通细节留给工作阶段 |
| 明确提出任务却一直聊、迟迟没有执行稿 | 本轮主动给完整精简提示词及选型，不要求另说“输出提示词” |
| 项目进行到一半，不知下一步做什么 | 关联后每轮先读取最新进展，再据此讨论、修订或建议下一步 |

它尤其适合语音输入、边想边说、需求经常变化、需要多轮整理的场景。简单而明确的问题直接问 Codex 就可以，不必额外启用它。

## 怎么用：从一句话开始

在 Codex 新对话里明确调用 skill，然后像平常说话一样描述目标：

~~~text
$task-clarifier

我想做一个社团活动报名小程序。社员主要用手机报名，社长需要管理报名名单。我还没想全，先帮我把需求理顺，暂时不要写代码。
~~~

接下来不用重新组织一整段提示词，直接继续说：

~~~text
补充：同一个人不能重复报名。
~~~

~~~text
纠正一下，报名名单只有社长能看；社员只能看到自己的报名状态。
~~~

~~~text
候补按提交时间排序，这点也加上。
~~~

你明确提出任务，或目标和重要范围已足够清楚，Task Clarifier 就会把兼容要求合并成一份**精简完整提示词**，同时给出具体模型名、推理强度和必要的协作建议。也可以随时说“输出提示词”；说“先讨论，暂时别出提示词”则先讨论。你决定何时复制到工作对话继续推进。

例如，“我需要一份完整的存档管理需求文档”会生成让工作对话撰写文档的提示词；无需先把文档每条规则都聊完，也不会在讨论对话直接替工作模型写完整文档。

> **不用特殊格式，也不用先学会写提示词。** “补充”“纠正”“输出提示词”“下一步”都可以直接说。

## 一个完整的小例子

你先说：

~~~text
我想给社团做个活动报名小程序。手机上要方便报名，社长要能看名单。先整理需求，不要写代码。
~~~

之后想到再补充：

~~~text
同一个活动不能重复报名。名单只有社长能看，社员只能看自己的报名状态。
~~~

Task Clarifier 把这些信息合成同一份草稿：

- 目标：社团活动报名小程序
- 使用者：社团成员和社长
- 成员端：手机报名，只能查看自己的提交状态
- 管理端：社长查看报名名单
- 规则：同一活动不可重复报名
- 当前边界：先整理需求，不写代码

**最终交给工作对话的提示词可能是：**

~~~text
请根据以下已确认需求，整理一个社团活动报名小程序的 MVP 方案，先不要写代码。
成员需要能在手机上报名；同一成员不能对同一活动重复报名；报名名单仅社长可见，成员只能查看自己的提交状态。
如果名额满后的候补规则会影响方案，请先列为待确认问题，不要替我假设。
~~~

这就是交接的价值：工作对话收到的是合并过的完整要求，而不是要自己从聊天记录里拼凑的零散补充。推荐模型和推理强度会结合任务及当前可选设置给出。

## 为什么不直接用普通聊天？

普通聊天也能整理需求。Task Clarifier 的特别之处，是把**持续讨论、需求版本维护、提示词编写和模型选择**作为一条连贯流程：

- **不要求一次说完**：想到的新内容可以随时加进同一份草稿。
- **改一处，不丢其他要求**：更新明确纠正的内容，保留兼容的旧约束。
- **不为小细节卡住**：优先澄清会改变任务方向的问题。
- **交接内容完整**：提示词可单独复制，不依赖工作对话去翻找前面的讨论。
- **区分建议和完成**：需求草稿、用户认可和实际执行不会混为一谈。
- **“下一步”看当前进度**：适用时核对关联项目的最新进展，不把旧摘要冒充新读取的状态。

## 它如何工作？

~~~mermaid
flowchart TB
    A["明确调用 Skill"] --> B["判断本轮意图与当前需求状态"]
    B --> C["维护目标、约束、未知项和最新草稿"]
    C --> D{"有影响任务方向的关键未知项？"}
    D -- "有" --> E["围绕关键分歧讨论或提问"]
    E --> C
    D -- "没有" --> F["输出完整、可修改的工作提示词"]
    F --> G["结合任务推荐模型与推理强度"]
    G --> H["由你决定何时复制到工作对话"]
    H -. "补充 / 纠正 / 下一步" .-> C
~~~

几个部分各司其职：

1. **SKILL.md** 定义讨论角色、需求整理流程、模型路由和输出格式。
2. **references/** 补充需求澄清、口述整理、模型选择、协作判断和状态恢复方法。
3. **session_mode.py** 可接收受支持的 Codex Hook 事件，登记当前对话是否处于需求讨论模式。
4. 如果你自行配置并信任 Hook，后续事件可按当前对话 UUID 恢复模式状态。
5. **需求正文仍在 Codex 对话上下文中。** Hook 状态文件记录当前对话 UUID、启用状态、来源、更新时间和可选工作对话 UUID，不保存需求正文、读取结果或聊天内容。

Hook 是可选的，需要用户在 Codex 环境中自行配置并信任；仓库不会自动更改 Codex 设置或安装 Hook。Hook 帮助恢复模式和关联，不能找回已经丢失的聊天历史，也不能代替每轮实际读取。更名后请核对命令中的脚本路径；命令变更需 Codex 正常审阅。

## 安装

把整个仓库目录放进 Codex 的 skills 目录，保留 **SKILL.md**、**agents/**、**references/** 和 **scripts/** 的相对结构：

- 设置了 **CODEX_HOME**：放到 **CODEX_HOME/skills/task-clarifier/**
- 未设置时通常放到 **~/.codex/skills/task-clarifier/**

安装后，在新对话开头明确调用 **$task-clarifier**。

## 行为边界与隐私

- 可明确调用 Skill，也可由模型按需求澄清与交接意图选择；Hook 只自动登记明确调用，语义选择需模型补登记。引用、代码块或聊天标题中的调用文字不会单独启用。
- 默认交付需求草稿和工作提示词，不会因为“继续”“实现”或“下一步”就擅自修改项目或启动任务。
- “下一步”需要读取最新项目进度时，只能依据当前可访问的对话或项目材料；读不到会说明缺口。
- Hook 状态文件不含需求正文；它无法代替对话历史，也不能恢复已丢失的聊天内容。
- 模型与计费参考会随产品变化；使用时应按当前可选模型和实际设置核对。

## 仓库结构

| 路径 | 用途 |
|---|---|
| **SKILL.md** | 主工作流程、模式边界与输出契约 |
| **agents/openai.yaml** | 技能展示名称、描述与默认调用提示 |
| **references/requirements-dialogue.md** | 连续讨论、需求状态与下一步 |
| **references/prompt-writing.md** | 围绕目标写精简完整的执行提示词 |
| **references/model-routing.md** | 模型、推理强度、速度和综合成本的选择 |
| **references/benchmark-evidence.md** | 带日期的模型与计费证据快照 |
| **references/hybrid-delegation.md** | 单模型与混合协作的比较方法 |
| **references/session-persistence.md** | Hook、状态登记、恢复与核验边界 |
| **references/active-project.md** | 用户本地填写的活动项目对话指针模板 |
| **scripts/session_mode.py** | Hook 事件解析与每对话状态辅助脚本 |
| **tests/test_session_mode.py** | 隔离的状态转换、关联和 Hook 事件回归测试 |
| **tests/behavior-cases.md** | 基于实际使用问题的真实对话验收场景 |

## 验证

运行 `python -X utf8 -B -m unittest discover -s tests -v` 检查状态与 Hook 行为。模型是否实际读取关联对话、及时交稿、保持提示词精简，需要在真实讨论对话按 [行为场景](tests/behavior-cases.md) 检查，不能用脚本通过替代。

## English

**Task Clarifier turns an unfinished request into a clear, concise prompt and recommends a suitable model and reasoning effort.** Start with voice or text, add details as they occur to you, and correct misunderstandings without rebuilding the prompt from scratch. Explicit work requests and sufficiently clear tasks receive a copy-ready prompt in the same turn; you do not need to separately ask for a prompt. It asks only about essential scope ambiguities and respects requests to discuss first. A request to write a requirements document produces a prompt for the work chat to write it.

~~~mermaid
flowchart LR
    A["Speak or type an unfinished idea"] --> B["Build one evolving brief"]
    B --> C{"A decision-changing detail is missing?"}
    C -- "Yes: clarify only that point" --> D["You add or correct details"]
    D --> B
    C -- "No" --> E["Copy-ready prompt<br/>plus model and effort"]
    E --> F["You choose when to hand it to a work chat"]
    F -. "More details or next step" .-> B
~~~

Start a new Codex conversation with **$task-clarifier** and a natural request, such as “I want to plan a club event signup app. Help clarify the requirements first; do not write code yet.” Follow up with ordinary messages like “add this constraint,” “correction,” or “give me the final prompt.” You decide when to copy the result into a work conversation; the skill does not automatically execute project work.

See the Chinese sections above for the detailed walkthrough, installation, architecture, privacy boundaries, and repository contents.

## License

MIT. See [LICENSE](LICENSE).
