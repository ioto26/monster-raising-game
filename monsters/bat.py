from Skill import Skill, SkillNode, SkillTree

# --------------------
# 1. 個々のスキルを定義
# --------------------
# コウモリが持つ全てのスキルを辞書で定義します。
bat_skills = {
    'かぜおこし': Skill('かぜおこし', '風属性の全体攻撃', 'active', mp_cost=8, sp_cost=1, effect={'damage_type': 'magic', 'damage_multiplier': 1.1}),
    '吸血': Skill('吸血', 'ダメージの一部を吸収', 'passive', sp_cost=2, effect={'life_steal': 0.2}),
    '超音波': Skill('超音波', '敵のステータスを下げる', 'passive', sp_cost=3, effect={'debuff': {'physical_defense': -5, 'magic_defense': -5}}),
    '闇の霧': Skill('闇の霧', '敵の命中率を下げる', 'active', mp_cost=12, sp_cost=4, effect={'debuff': {'accuracy': -10}}),
    '夜行性': Skill('夜行性', '夜間に能力上昇', 'passive', sp_cost=5, effect={'conditional_buff': {'speed': 10}}),
    '超音波ブレス': Skill('超音波ブレス', '全体に音波攻撃と状態異常', 'active', mp_cost=25, sp_cost=8, effect={'damage_type': 'magic', 'damage_multiplier': 1.5, 'status_effect': 'deaf' })
}

# -----------------------------------
# 2. スキルツリーのノードを定義
# -----------------------------------
# ツリー内のノードを辞書で管理し、後から前提条件を設定します。
bat_nodes = {
    'かぜおこし': SkillNode(bat_skills['かぜおこし']),
    '吸血': SkillNode(bat_skills['吸血']),
    '超音波': SkillNode(bat_skills['超音波']),
    '闇の霧': SkillNode(bat_skills['闇の霧']),
    '夜行性': SkillNode(bat_skills['夜行性']),
    '超音波ブレス': SkillNode(bat_skills['超音波ブレス'])
}

# ------------------------------------
# 3. ノード間の前提条件を設定
# ------------------------------------
# 各スキルの前提スキルを、対応するノードオブジェクトで指定します。
bat_nodes['吸血'].prerequisites.append(bat_nodes['かぜおこし'])
bat_nodes['超音波'].prerequisites.append(bat_nodes['吸血'])
bat_nodes['闇の霧'].prerequisites.append(bat_nodes['超音波'])
bat_nodes['夜行性'].prerequisites.append(bat_nodes['吸血'])
bat_nodes['超音波ブレス'].prerequisites.append(bat_nodes['闇の霧'])
bat_nodes['超音波ブレス'].prerequisites.append(bat_nodes['夜行性'])

# ------------------------------------
# 4. SkillTreeインスタンスを作成し外部へ公開
# ------------------------------------
# Monsterクラスがインポートできるように、最終的なSkillTreeインスタンスを作成します。
bat_tree = SkillTree('コウモリの奥義', list(bat_nodes.values()))

# このファイルからインポートされるものを明示的に指定します。
__all__ = ['bat_tree']