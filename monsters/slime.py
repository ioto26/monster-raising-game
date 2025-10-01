# slime.py

from Skill import Skill, SkillNode, SkillTree

# 1. 個々のスキルを定義
slime_skills = {
    'ぷるぷるボディ': Skill('ぷるぷるボディ', '物理ダメージ軽減', 'passive', sp_cost=1, effect={"physical_defense": 5}),
    '液体化': Skill('液体化', '物理攻撃の確率回避', 'passive', sp_cost=2, effect={"dodge_rate": 0.1}),
    'ヒール': Skill('ヒール', '自分のHPを回復', 'active', mp_cost=10, sp_cost=3, effect={"heal": 30}),
    '身代わり': Skill('身代わり', '味方への攻撃を肩代わり', 'active', mp_cost=15, sp_cost=5, effect={"protect": True}),
    'メタルボディ': Skill('メタルボディ', '防御力大幅上昇', 'passive', sp_cost=7, effect={"physical_defense": 15, "speed": -5}),
    '合体': Skill('合体', '一時的なステータス大幅上昇', 'active', mp_cost=30, sp_cost=10, effect={"type":"buff", "physical_attack": 10, "physical_defense": 10, "speed": 10, "duration": 3})
}

# 2. SkillNodeインスタンスを全て事前に作成し、辞書で管理
slime_nodes = {
    'ぷるぷるボディ': SkillNode(slime_skills['ぷるぷるボディ']),
    '液体化': SkillNode(slime_skills['液体化']),
    'ヒール': SkillNode(slime_skills['ヒール']),
    '身代わり': SkillNode(slime_skills['身代わり']),
    'メタルボディ': SkillNode(slime_skills['メタルボディ']),
    '合体': SkillNode(slime_skills['合体'])
}

# 3. ノード間の前提条件を明確に設定
# 各ノードのprerequisitesリストに、正しい前提ノードオブジェクトを追加
slime_nodes['液体化'].prerequisites.append(slime_nodes['ぷるぷるボディ'])
slime_nodes['ヒール'].prerequisites.append(slime_nodes['液体化'])
slime_nodes['身代わり'].prerequisites.append(slime_nodes['ヒール'])
slime_nodes['メタルボディ'].prerequisites.append(slime_nodes['液体化'])
slime_nodes['合体'].prerequisites.append(slime_nodes['身代わり'])
slime_nodes['合体'].prerequisites.append(slime_nodes['メタルボディ'])

# 4. SkillTreeインスタンスを作成し外部へ公開
slime_tree = SkillTree('スライムの奥義', list(slime_nodes.values()))

__all__ = ['slime_tree']