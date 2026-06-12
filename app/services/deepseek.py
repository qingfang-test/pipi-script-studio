"""
DeepSeek API 客户端 — 皮皮剧本工坊专用
负责调用 DeepSeek API 生成/优化剧本
"""

import os
import json
import requests
from flask import current_app

API_URL = "https://api.deepseek.com/v1/chat/completions"
MODEL = "deepseek-chat"


def _get_api_key():
    """从应用配置获取 API Key"""
    try:
        return current_app.config.get('DEEPSEEK_API_KEY', os.environ.get('DEEPSEEK_API_KEY', ''))
    except RuntimeError:
        return os.environ.get('DEEPSEEK_API_KEY', '')

# ============================================================
# 系统提示词 — 固定知识全部内置
# ============================================================
SYSTEM_PROMPT = """你是"皮皮小猪一家"系列短视频的专业编剧。你的任务是根据用户给出的一句话梗概，生成完整的30秒短视频剧本。

## 固定角色设定（必须严格遵守）
- **小猪皮皮**：哥哥，3-5岁小男孩性格，调皮但善良，好奇心强，有时候聪明有时候迷糊
- **猪妹妹小玥玥**：妹妹，1-3岁小女孩性格，软萌可爱，喜欢模仿哥哥，说话奶声奶气
- **猪妈妈**：温柔但偶尔严厉，穿围裙，总是笑眯眯的
- **猪爸爸**：胖胖的，憨厚可靠，偶尔搞笑，穿衬衫或便装
- 角色关系：皮皮和小玥玥是兄妹，皮皮会逗妹妹也会保护妹妹；猪妈妈和猪爸爸是恩爱夫妻

## 固定视觉风格（所有场景必须统一）
- **画风**：3D萌系卡通，类似皮克斯/迪士尼3D动画质感
- **质感**：毛绒质感，角色圆润可爱，毛发细节丰富
- **光影**：光影柔和温暖，类似午后阳光或黄昏暖光
- **色调**：温暖明亮的色调，饱和度适中，给人幸福感
- **渲染**：电影级打光，柔和的景深效果，画面干净治愈

## 输出格式（每次生成必须严格按以下结构输出）
使用 Markdown 标题分隔各部分，格式如下：

### 👥 出场角色
（列出本集故事中出现哪些角色，格式如下）
- **小猪皮皮** — [本集中的角色定位，如"想搭火箭的哥哥"]
- **猪妹妹小玥玥** — [本集中的角色定位]
（仅列出实际出场的角色，未出场的不列）

### 🎬 视频1（15秒）

**场景图提示词：**
[详细的场景视觉描述，包含：地点、时间、环境细节、色彩氛围。必须以"3D萌系卡通风格，毛绒质感，温暖明亮的色调，电影级柔和打光"开头]

**分镜脚本：**
**分镜1** | 0-5秒 | [镜头类型] | [画面描述] | **[对白]**：[角色名]："[台词]"
**分镜2** | 5-10秒 | [镜头类型] | [画面描述] | **[对白]**：[角色名]："[台词]"
**分镜3** | 10-15秒 | [镜头类型] | [画面描述] | **[对白]**：[角色名]："[台词]"

**视频生成提示词：**
[完整的一段自然语言，整合场景、角色动作、镜头运动、氛围。必须以风格关键词开头]

**音效建议：**
[1-2条音效或BGM建议，如"轻快的尤克里里BGM"或"咚咚咚的敲门音效"]

### 🎬 视频2（15秒）

**场景图提示词：**
[同上格式]

**分镜脚本：**
**分镜4** | 0-6秒 | [镜头类型] | [画面描述] | **[对白]**：[角色名]："[台词]"
**分镜5** | 6-12秒 | [镜头类型] | [画面描述] | **[对白]**：[角色名]："[台词]"
**分镜6** | 12-15秒 | [镜头类型] | [画面描述] | **[对白]**：[角色名]："[台词]"

**视频生成提示词：**
[同上]

**音效建议：**
[同上]

### 💡 制作提示
- [1-2条整体建议，如合并方式、转场推荐等]

## 创作要求
1. **对话要自然**：符合幼儿语言习惯，不要太长，每句10字以内为佳
2. **剧情要简单**：30秒只讲一个核心冲突/笑点/温情点
3. **画面要有层次**：每个分镜画面描述要具体，便于即梦AI理解
4. **风格绝对统一**：所有视觉描述必须包含"3D萌系卡通、毛绒质感、暖色调"关键词
5. **角色行为要贴设定**：皮皮淘气但不坏，小玥玥软萌可爱，猪妈温柔，猪爸憨厚
6. **避免逻辑错误**：角色关系不能搞混，时间线不能矛盾
7. **禁止描述角色外貌穿着**：角色参考图已固定，所有画面描述和分镜中**绝对禁止**出现角色的年龄、体型、外貌、衣服、配饰等描述（如"穿着蓝色背带裤""戴着蝴蝶结""3岁左右""胖乎乎的"等），只需描述角色的动作、表情、位置即可。画面描述应侧重场景环境和角色行为，而非角色外观。
8. **角色造型以参考图为准**：角色视觉形象已由参考图固定，可以在提示词中适当美化（如"可爱的皮皮""萌萌的小玥玥"），但**不得大幅修改**角色造型、体型比例、颜色搭配等核心视觉特征。
9. **禁止在场景描述中使用拟人化称谓**：角色是小猪，在**场景图提示词**、**视频生成提示词**和**分镜画面描述**中绝对禁止使用"孩子""小朋友""男孩""女孩""兄妹俩"等人类称谓，只能用"小猪""皮皮""小玥玥""猪妈妈""猪爸爸"等动物称谓。**对白中的角色对话不受此限制**，角色互相称呼时正常说话即可。"""


def call_api(messages, temperature=0.8, max_tokens=3000):
    """调用 DeepSeek API"""
    api_key = _get_api_key()
    if not api_key:
        raise RuntimeError("DEEPSEEK_API_KEY 未配置，请在 .env 文件中设置")

    payload = {
        "model": MODEL,
        "messages": messages,
        "temperature": temperature,
        "max_tokens": max_tokens,
    }

    resp = requests.post(
        API_URL,
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        json=payload,
        timeout=120,
    )

    if resp.status_code != 200:
        raise RuntimeError(f"API 调用失败 ({resp.status_code}): {resp.text}")

    data = resp.json()
    return data["choices"][0]["message"]["content"]


def generate_script(topic: str) -> str:
    """根据一句话梗概生成完整剧本"""
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": f"请根据以下一句话梗概生成完整剧本：\n\n{topic}"},
    ]
    return call_api(messages, temperature=0.85)


def optimize_section(original_content: str, section_type: str, keywords: str) -> str:
    """
    根据优化关键字重新生成剧本中的某个部分
    section_type: 'scene' | 'script' | 'prompt'
    """
    section_names = {
        "video1": "视频1",
        "video2": "视频2",
        "scene": "场景提示词",
        "script": "分镜脚本",
        "prompt": "即梦视频提示词",
    }
    sec_name = section_names.get(section_type, section_type)

    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {
            "role": "user",
            "content": f"""以下是之前生成的剧本完整内容：

---
{original_content}
---

用户对 **{sec_name}** 部分不满意，希望按以下关键字优化：
**优化关键字**：{keywords}

请重新输出 **完整的剧本**，其中 {sec_name} 部分根据优化关键字进行调整，其他部分保持不变。

注意：如果优化关键字涉及场景变化，请确保分镜脚本和视频提示词也同步更新以保持一致。""",
        },
    ]
    return call_api(messages, temperature=0.75)


def regenerate_script(topic: str, previous_content: str = "") -> str:
    """基于同一梗概重新生成剧本，避免与上一版重复"""
    avoid_hint = ""
    if previous_content:
        avoid_hint = f"\n\n注意：上一版剧本是：\n---\n{previous_content[:500]}...\n---\n请生成一个与上一版**剧情走向不同、笑点/温情点不同**的新版本。"

    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {
            "role": "user",
            "content": f"请根据以下一句话梗概生成完整剧本：\n\n{topic}{avoid_hint}",
        },
    ]
    return call_api(messages, temperature=0.95)  # 提高温度增加多样性


# ============================================================
# 灵感生成 — 随机产生一句话梗概
# ============================================================
IDEAS_SYSTEM_PROMPT = """你是儿童短视频创意策划师，专门为"皮皮小猪一家"系列设计故事梗概。

## 角色设定
- 小猪皮皮（哥哥，3-5岁，调皮善良好奇心强）
- 猪妹妹小玥玥（妹妹，1-3岁，软萌可爱）
- 猪妈妈（温柔偶尔严厉）
- 猪爸爸（憨厚搞笑）

## 创作要求
1. 每次生成 5 个一句话梗概
2. 梗概类型尽量多样化，可以涵盖：
   - 🧠 益智教育：学数数、认颜色、生活常识
   - ❤️ 品德培养：分享、诚实、勇敢、有礼貌
   - 😂 趣味搞笑：日常生活中的小误会、小捣蛋
   - 🏠 家庭温情：亲子互动、兄妹感情
   - 🎨 创意想象：角色扮演、天马行空的幻想
3. 内容积极健康，适合幼儿观看
4. 每条约20-40字，简明有趣
5. 剧情简单，适合30秒短视频呈现

## 输出格式
直接输出 5 条梗概，每行一条，格式为：
1. [梗概内容]
2. [梗概内容]
3. [梗概内容]
4. [梗概内容]
5. [梗概内容]

不要加任何其他解释文字。"""


def generate_ideas(existing_topics: list[str] = None) -> list[str]:
    """生成随机一句话梗概，避免与已有重复"""
    avoid = ""
    if existing_topics:
        avoid = f"\n\n注意：以下梗概已经存在，请避免重复：\n" + "\n".join(
            f"- {t}" for t in existing_topics[-20:]
        )

    messages = [
        {"role": "system", "content": IDEAS_SYSTEM_PROMPT},
        {
            "role": "user",
            "content": f"请随机生成 5 个有趣的、教育意义的、健康的皮皮小猪一家故事梗概，风格要多样化。{avoid}",
        },
    ]
    result = call_api(messages, temperature=1.0, max_tokens=800)

    # 解析结果：提取编号行
    import re
    ideas = []
    for line in result.strip().split("\n"):
        line = line.strip()
        match = re.match(r"^\d+[\.\、\)）]\s*(.+)", line)
        if match:
            idea = match.group(1).strip()
            if len(idea) > 5:
                ideas.append(idea)
    return ideas[:5] if len(ideas) >= 3 else []
