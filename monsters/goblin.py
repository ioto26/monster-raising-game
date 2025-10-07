# このファイルは、ゴブリン専用のスキルとスキルツリーを定義します。
# Monsterクラスがこのファイルを動的にインポートして利用します。

from Skill import Skill, SkillNode, SkillTree

# --------------------
# 1. 個々のスキルを定義
# --------------------
# ゴブリンが持つ全てのスキルを辞書で定義します。
goblin_skills = {
    'なげナイフ': Skill('なげナイフ', '遠距離攻撃', 'active', mp_cost=5, sp_cost=1, effect={"damage_type": "physical", "damage_multiplier": 1.2}),
    'いたずら': Skill('いたずら', '敵に状態異常付与', 'active', mp_cost=8, sp_cost=2, effect={"type": "ailment", "ailment_chance": 0.8, "ailment_type": ["confusion", "stun"], "duration": 2}),
    '連携攻撃': Skill('連携攻撃', '仲間と追加攻撃', 'passive', sp_cost=3, effect={"extra_attack_chance": 0.3, "trigger": "ally_attack"}),
    '隠密行動': Skill('隠密行動', '敵に発見されにくくなる', 'passive', sp_cost=4, effect={"stealth": True, "detection_rate": -0.2}),
    'リーダーシップ': Skill('リーダーシップ', '仲間の攻撃力上昇', 'passive', sp_cost=5, effect={"type": "buff", "physical_attack": 5, "duration": 3}),
    '突撃': Skill('突撃', '自身と敵にダメージ', 'active', mp_cost=15, sp_cost=7, effect={"damage_type": "physical", "damage_multiplier": 2.0, "self_damage": 30})
}

# -----------------------------------
# 2. スキルツリーのノードを定義
# -----------------------------------
# ツリー内のノードを辞書で管理し、後から前提条件を設定します。
goblin_nodes = {
    'なげナイフ': SkillNode(goblin_skills['なげナイフ']),
    'いたずら': SkillNode(goblin_skills['いたずら']),
    '連携攻撃': SkillNode(goblin_skills['連携攻撃']),
    '隠密行動': SkillNode(goblin_skills['隠密行動']),
    'リーダーシップ': SkillNode(goblin_skills['リーダーシップ']),
    '突撃': SkillNode(goblin_skills['突撃'])
}

# ------------------------------------
# 3. ノード間の前提条件を設定
# ------------------------------------
# 各スキルの前提スキルを、対応するノードオブジェクトで指定します。
goblin_nodes['いたずら'].prerequisites.append(goblin_nodes['なげナイフ'])
goblin_nodes['連携攻撃'].prerequisites.append(goblin_nodes['なげナイフ'])
goblin_nodes['隠密行動'].prerequisites.append(goblin_nodes['いたずら'])
goblin_nodes['リーダーシップ'].prerequisites.append(goblin_nodes['連携攻撃'])
goblin_nodes['突撃'].prerequisites.append(goblin_nodes['隠密行動'])
goblin_nodes['突撃'].prerequisites.append(goblin_nodes['リーダーシップ'])

# ------------------------------------
# 4. SkillTreeインスタンスを作成し外部へ公開
# ------------------------------------
# Monsterクラスがインポートできるように、最終的なSkillTreeインスタンスを作成します。
goblin_tree = SkillTree('ゴブリンの奥義', list(goblin_nodes.values()))

# このファイルからインポートされるものを明示的に指定します。
__all__ = ['goblin_tree']