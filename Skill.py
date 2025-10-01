# Skill.py

class Skill:
    def __init__(self, name, description, category, mp_cost=0, sp_cost=0, effect=None):
        """
        個々のスキルを表すクラス
        :param name: スキル名（例: 'メラ', '攻撃力アップ'）
        :param description: スキルの説明
        :param category: スキルの種類（例: 'attack', 'status_up', 'passive', 'support'）
        :param mp_cost: 消費MP
        :param sp_cost: 習得に必要なスキルポイント
        :param effect: スキルがもたらす効果（辞書形式で定義）
        """
        self.name = name
        self.description = description
        self.category = category
        self.mp_cost = mp_cost
        self.sp_cost = sp_cost
        self.effect = effect or {} # 例: {'damage': 10, 'element': 'fire'}, {'status': 'attack', 'amount': 5}
        self.unlocked = False # 習得済みかどうか
        
class SkillNode:
    def __init__(self, skill: Skill, prerequisites=None):
        """
        スキルツリー内のノードを表すクラス
        :param skill: このノードが持つSkillオブジェクト
        :param prerequisites: このスキルを習得するために必要なSkillNodeのリスト
        """
        self.skill = skill
        # デフォルト引数がNoneの場合に、新しいリストを作成する
        self.prerequisites = prerequisites if prerequisites is not None else []

class SkillTree:
    def __init__(self, name, nodes):
        """
        スキルツリー全体を管理するクラス
        :param name: ツリー名（例: '炎の極意', '守護者の誓い'）
        :param nodes: ツリー内の全てのSkillNodeのリスト
        """
        self.name = name
        self.nodes = {node.skill.name: node for node in nodes}
        self.total_points = 0
        self.unlocked_skills = set()

    def learn_skill(self, skill_name, monster_skill_points):
        """
        モンスターのスキルポイントが足りているかなどをチェックし、
        習得成功時に必要なスキルポイントを返します。
        :param skill_name: 習得したいスキルの名前
        :param monster_skill_points: モンスターが持つスキルポイント
        :return: 習得成功時に消費するポイント、失敗時はNone
        """
        if skill_name not in self.nodes:
            print(f"Error: {skill_name} はこのツリーに存在しません。")
            return None

        skill_to_unlock = self.nodes[skill_name].skill
        required_points = skill_to_unlock.sp_cost

        # 習得済みチェック
        if skill_to_unlock.unlocked:
            print(f"Warning: {skill_name} は既に習得済みです。")
            return None

        # スキルポイントチェック
        if monster_skill_points < required_points:
            print(f"Error: スキルポイントが{required_points}必要です。（現在: {monster_skill_points}）")
            return None

        # 前提スキルチェック
        prerequisites_met = all(prereq.skill.unlocked for prereq in self.nodes[skill_name].prerequisites)
        if not prerequisites_met:
            print(f"Error: {skill_name} の前提スキルがまだ習得されていません。")
            return None

        # 習得成功
        self.unlocked_skills.add(skill_name)
        skill_to_unlock.unlocked = True
        print(f"Info: {skill_name} を習得しました！")
        return required_points