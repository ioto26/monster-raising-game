from Skill import Skill, SkillNode, SkillTree

# --------------------
# 1. 個々のスキルを定義
# --------------------
# オオカミが持つ全てのスキルを辞書で定義します。
wolf_skills = {
    '俊足': Skill('俊足', '素早さ上昇', 'passive', sp_cost=1, effect={'speed': 5}),
    'かみつき': Skill('かみつき', '敵単体攻撃', 'active', mp_cost=5, sp_cost=2, effect={'damage_type':'physical', 'damage_multiplier': 1.2}),
    '追撃': Skill('追撃', '確率で追加攻撃', 'passive', sp_cost=3, effect={'extra_attack_chance': 0.3, 'damage_multiplier': 0.5}),
    '三連牙': Skill('三連牙', '敵に3回連続攻撃', 'active', mp_cost=15, sp_cost=5, effect={'damage_type':'physical', 'damage_multiplier': 0.5, 'hits': 3}),
    '血の匂い': Skill('血の匂い', 'HPの減った敵に攻撃力上昇', 'passive', sp_cost=4, effect={'physical_attack': 5, 'enemy_hp_below': 50}),
    'ハウリング': Skill('ハウリング', '仲間の攻撃力上昇', 'active', mp_cost=20, sp_cost=8, effect={'buff': 'all_attack_up', 'amount': 10, 'duration': 3})
}

# -----------------------------------
# 2. スキルツリーのノードを定義
# -----------------------------------
# ツリー内のノードを辞書で管理し、後から前提条件を設定します。
wolf_nodes = {
    '俊足': SkillNode(wolf_skills['俊足']),
    'かみつき': SkillNode(wolf_skills['かみつき']),
    '追撃': SkillNode(wolf_skills['追撃']),
    '三連牙': SkillNode(wolf_skills['三連牙']),
    '血の匂い': SkillNode(wolf_skills['血の匂い']),
    'ハウリング': SkillNode(wolf_skills['ハウリング'])
}

# ------------------------------------
# 3. ノード間の前提条件を設定
# ------------------------------------
# 各スキルの前提スキルを、対応するノードオブジェクトで指定します。
wolf_nodes['かみつき'].prerequisites.append(wolf_nodes['俊足'])
wolf_nodes['追撃'].prerequisites.append(wolf_nodes['かみつき'])
wolf_nodes['三連牙'].prerequisites.append(wolf_nodes['追撃'])
wolf_nodes['血の匂い'].prerequisites.append(wolf_nodes['かみつき'])
wolf_nodes['ハウリング'].prerequisites.append(wolf_nodes['三連牙'])
wolf_nodes['ハウリング'].prerequisites.append(wolf_nodes['血の匂い'])

# ------------------------------------
# 4. SkillTreeインスタンスを作成し外部へ公開
# ------------------------------------
# Monsterクラスがインポートできるように、最終的なSkillTreeインスタンスを作成します。
wolf_tree = SkillTree('オオカミの奥義', list(wolf_nodes.values()))

# このファイルからインポートされるものを明示的に指定します。
__all__ = ['wolf_tree']