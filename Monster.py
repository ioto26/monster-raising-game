import random
import importlib
import os
import sys
import json

class Monster:
    MONSTER_MAPPING = {
        "スライム": "slime",
        "ゴブリン": "goblin",
        "オオカミ": "wolf",
        "コウモリ": "bat",
    }

    def __init__(self, name, max_hp, max_mp, physical_attack, physical_defense, magic_attack, magic_defense, speed, 
                enemy_exp=20, enemy_gold=15, scout_rate=0.1,
                growth_rate={'HP':1.2, 'MP':1.1, 'Physical_Attack':1.1, 'Physical_Defense':1.1, 'Magic_Attack':1.1, 'Magic_Defense':1.1,  'Speed':1.1}, ability=None):
        self.name = name
        self.max_hp = max_hp
        self.current_hp = max_hp  # 現在のHP
        self.max_mp = max_mp
        self.current_mp = max_mp  # 現在のMP
        self.physical_attack = physical_attack
        self.physical_defense = physical_defense
        self.magic_attack = magic_attack
        self.magic_defense = magic_defense
        self.speed = speed
        self.dodge_rate = 0.05  # 回避率
        self.growth_rate = growth_rate

        self.is_alive = True
        self.is_defending = False
        self.is_guarding = False

        self.level = 1
        self.experience = 0
        self.need_experience = 10  # 次のレベルに必要な経験値
        self.experience_ratio = 1.5  # 経験値の増加率

        self.enemy_exp = enemy_exp # このモンスターを倒したときに得られる経験値
        self.enemy_gold = enemy_gold # このモンスターを倒したときに得られるゴールド
        self.scout_rate = scout_rate # スカウト成功率

        self.skills = []
        self.skill_points = 0
        self.skill_trees = self.load_skill_tree()

        self.ability = ability  # 特性（未実装）

        self.status_effects = {}

        self.buffs = {}      # 例: {'physical_attack_up': {'duration': 3, 'value': 1.5, 'original_stat': 50}, ...}
        self.debuffs = {}    # 例: {'physical_defense_down': {'duration': 2, 'value': 0.5, 'original_stat': 20}, ...}
        self.ailments = {}   # 例: {'poison': {'duration': 4, 'damage_percent': 0.1}, 'burn': {'duration': 3, 'damage': 5}}
        
        # --- 追加点: 元のステータスを保持するための属性 ---
        # 永続的なステータス（ベース値）
        self.base_max_hp = max_hp
        self.base_max_mp = max_mp
        self.base_physical_attack = physical_attack
        self.base_physical_defense = physical_defense
        self.base_magic_attack = magic_attack
        self.base_magic_defense = magic_defense
        self.base_speed = speed
    
    @classmethod
    def load_monster_data(cls, name):
        """
        JSONファイルから指定されたモンスターのデータをロードする
        """
        # 現在のファイルのディレクトリを取得
        base_path = os.path.dirname(os.path.abspath(__file__))
        data_path = os.path.join(base_path, 'data', 'monster_stats.json')
        
        # 'data'ディレクトリがMonster.pyと同じ階層になく、プロジェクトのルートにある場合はパスを変更してください
        # 例: data_path = os.path.join(os.path.abspath(os.path.join(base_path, os.pardir)), 'data', 'monster_stats.json')
        
        try:
            with open(data_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            if name not in data:
                raise ValueError(f"Error: {name} のデータがJSONファイルに見つかりません。")
            
            return data[name]
            
        except FileNotFoundError:
            print(f"Error: JSONファイル {data_path} が見つかりません。")
            sys.exit(1)
        except json.JSONDecodeError:
            print(f"Error: JSONファイル {data_path} のフォーマットが不正です。")
            sys.exit(1)

    @classmethod
    def from_json(cls, name):
        """
        JSONデータを使用してMonsterインスタンスを作成するファクトリメソッド
        """
        monster_data = cls.load_monster_data(name)

        return cls(
            name=name,
            max_hp=monster_data['max_hp'],
            max_mp=monster_data['max_mp'],
            physical_attack=monster_data['physical_attack'],
            physical_defense=monster_data['physical_defense'],
            magic_attack=monster_data['magic_attack'],
            magic_defense=monster_data['magic_defense'],
            speed=monster_data['speed'],
            enemy_exp=monster_data['enemy_exp'],
            enemy_gold=monster_data['enemy_gold'],
            scout_rate=monster_data['scout_rate'],
            growth_rate=monster_data['growth_rate']
        )

    def take_damage(self, damage):
        self.current_hp -= damage
        if self.current_hp <= 0:
            self.current_hp = 0
            self.is_alive = False
        print(f"{self.name}は{damage}のダメージを受けた！")

    def is_fainted(self):
        return self.is_alive == False

    def get_next_level_exp(self):
        """
        指定されたレベルから次のレベルに上がるために必要な経験値を計算する
        """
        if self.level < 1:
            return 0  # 負のレベルはありえないので
        
        # 等比数列の公式を使用
        next_experience = self.need_experience * (self.experience_ratio ** (self.level - 1))
        return next_experience
    
    def gain_experience(self, exp):
        self.experience += exp
        print(f"{self.name}は{exp}の経験値を得た！")
        
        # 経験値が次のレベルに必要な値を超えているかチェック
        while self.experience >= self.get_next_level_exp():
            # 次のレベルに必要な経験値を経験値から引いてからレベルアップ
            self.experience -= self.get_next_level_exp()
            self.level_up()

    def level_up(self):
        self.level += 1
        self.max_hp = int(self.max_hp * self.growth_rate['HP'] + random.randint(1, 3))
        self.current_hp = self.max_hp
        self.base_max_hp = self.max_hp

        self.max_mp = int(self.max_mp * self.growth_rate['MP'] + random.randint(1, 3))
        self.current_mp = self.max_mp
        self.base_max_mp = self.max_mp

        self.physical_attack = int(self.physical_attack * self.growth_rate['Physical_Attack'] + random.randint(1, 3))
        self.base_physical_attack = self.physical_attack

        self.physical_defense = int(self.physical_defense * self.growth_rate['Physical_Defense'] + random.randint(1, 3))
        self.base_physical_defense = self.physical_defense

        self.magic_attack = int(self.magic_attack * self.growth_rate['Magic_Attack'] + random.randint(1, 3))
        self.base_magic_attack = self.magic_attack

        self.magic_defense = int(self.magic_defense * self.growth_rate['Magic_Defense'] + random.randint(1, 3))
        self.base_magic_defense = self.magic_defense

        self.speed = int(self.speed * self.growth_rate['Speed'] + random.randint(1, 3))
        self.base_speed = self.speed

        print(f"{self.name}はレベル{self.level}に上がった！")
        print(f"HP: {self.max_hp}, MP: {self.max_mp}, 物理攻撃: {self.physical_attack}, 物理防御: {self.physical_defense}, 魔法攻撃: {self.magic_attack}, 魔法防御: {self.magic_defense}, すばやさ: {self.speed}")

        self.skill_points += 30 # 例: レベルが上がるごとに1ポイント獲得
        print(f"スキルポイントを1獲得した！ (合計: {self.skill_points})")

    def display_status(self):
        print(f"--- {self.name}のステータス ---")
        print(f"レベル: {self.level}")
        print(f"HP: {self.current_hp}/{self.max_hp} [{self.get_hp_bar()}]")
        print(f"MP: {self.current_mp}/{self.max_mp}")
        print(f"物理攻撃: {self.physical_attack}")
        print(f"物理防御: {self.physical_defense}")
        print(f"魔法攻撃: {self.magic_attack}")
        print(f"魔法防御: {self.magic_defense}")
        print(f"すばやさ: {self.speed}")
        print(f"経験値: {self.experience}/{self.get_next_level_exp()}")
        print(f"スキルポイント: {self.skill_points}")
        active_skills = self.get_active_skills()
        passive_skills = self.get_passive_skills()

        if active_skills:
            print("▶️ アクティブスキル:")
            for skill in active_skills:
                print(f"- {skill.name} (MP{skill.mp_cost}): {skill.description}")
        else:
            print("▶️ アクティブスキル: なし")

        if passive_skills:
            print("🛡️ パッシブスキル:")
            for skill in passive_skills:
                print(f"- {skill.name}: {skill.description}")
        else:
            print("🛡️ パッシブスキル: なし")

        print("-----------------------")

    def get_active_skills(self):
        """
        現在習得しているアクティブスキルをリストで返す
        """
        return [skill for skill in self.skills if skill.category == 'active']
    
    def get_passive_skills(self):
        """
        現在習得しているパッシブスキルをリストで返す
        """
        # self.skillsはSkillオブジェクトのリストと仮定
        return [skill for skill in self.skills if skill.category == 'passive']
    
    def load_skill_tree(self):
        module_name = self.MONSTER_MAPPING.get(self.name)
        if not module_name:
            print(f"Warning: モンスター '{self.name}' に対応するスキルツリーが見つかりません。")
            return []

        try:
            # monstersフォルダをsys.pathに追加
            base_path = os.path.dirname(os.path.abspath(__file__))
            monsters_path = os.path.join(base_path, 'monsters')
            if monsters_path not in sys.path:
                sys.path.insert(0, monsters_path)
            
            # モジュールをインポートし、必要なオブジェクトのみをグローバル空間に読み込む
            # from monsters.slime import slime_tree のように処理する
            module = importlib.import_module(f'monsters.{module_name}')
            skill_tree = getattr(module, f'{module_name}_tree')
            
            return [skill_tree]
        except (ImportError, AttributeError) as e:
            print(f"Warning: スキルツリー {self.name} の読み込みに失敗しました。詳細: {e}")
            return []
        
    def reset_status_to_base(self, status_key, original_value):
        """
        特定のステータスを一時効果適用前の値に戻す
        """
        if status_key == 'max_hp':
            self.max_hp = original_value
        elif status_key == 'max_mp':
            self.max_mp = original_value
        elif status_key == 'physical_attack':
            self.physical_attack = original_value
        elif status_key == 'physical_defense':
            self.physical_defense = original_value
        elif status_key == 'magic_attack':
            self.magic_attack = original_value
        elif status_key == 'magic_defense':
            self.magic_defense = original_value
        elif status_key == 'speed':
            self.speed = original_value
        elif status_key == 'dodge_rate':
            self.dodge_rate = original_value
        
    # --- 既存メソッド `apply_skill_effect` の変更 ---
    # `Battle.py` にあったものを修正して、バフ効果の適用時にベース値を記録し、効果を登録する
    def apply_buff_effect(self, skill_effect):
        duration = skill_effect.get('duration', 0)
        
        if duration <= 0:
            return
            
        for key, value in skill_effect.items():
            if key in ['physical_attack', 'physical_defense', 'magic_attack', 'magic_defense', 'speed', 'dodge_rate']:
                
                # すでに効果が適用中の場合は、durationをリセットし、効果を上書きする
                if key not in self.status_effects:
                    # ベース値を取得（例: physical_attackのベース値）
                    original_value = getattr(self, key)

                    # ベース値を記録
                    self.status_effects[key] = {
                        'type': 'buff',
                        'original_value': original_value,
                        'duration': duration,
                        'amount': value # 適用された効果量
                    }
                else:
                    # 既に効果が適用中の場合は、durationを更新するだけにする（複雑なロジックは避ける）
                    self.status_effects[key]['duration'] = duration
                    
                # モンスターのステータスに効果量を加算
                setattr(self, key, getattr(self, key) + value)
                
        print(f"🔰 {self.name}のステータスが{duration}ターン上昇した！")

    def apply_debuff_effect(self, skill_effect):
        duration = skill_effect.get('duration', 0)
        logs = [] # ログを保持するため

        if duration <= 0:
            return logs
            
        for key, value in skill_effect.items():
            # ステータスデバフの適用
            if key in ['physical_attack', 'physical_defense', 'magic_attack', 'magic_defense', 'speed', 'dodge_rate']:
                # すでに効果が適用中の場合は、durationをリセットし、効果を上書きする
                if key not in self.status_effects:
                    original_value = getattr(self, key)
                    self.status_effects[key] = {
                        'original_value': original_value,
                        'duration': duration,
                        'amount': -value # 適用された効果量（デバフなのでマイナス）
                    }
                else:
                    self.status_effects[key]['duration'] = duration
                    
                # モンスターのステータスに効果量を減算
                setattr(self, key, getattr(self, key) - value)
                logs.append(f"⬇️ {self.name}の**{key}**が{value}下がった！")

    def apply_ailment_effect(self, skill_effect):
        """
        スキルエフェクトから状態異常を抽出し、モンスターに適用する。
        """
        
        # typeが'ailment'でない場合は処理を終了
        if skill_effect.get('type') != 'ailment':
            return

        # --- 必要な基本情報の取得 ---
        # duration は必須情報なので、最初に取得
        duration = skill_effect.get('duration', 0)
        if duration <= 0:
            return 
            
        chance = skill_effect.get('ailment_chance', 1.0) # 成功率
        
        # ailment_type はリストまたは単一の文字列を想定
        ailment_candidates = skill_effect.get('ailment_type', [])
        if not ailment_candidates:
            return
        
        # --- 状態異常の適用判定 ---
        if random.random() < chance:
            
            # 候補からランダムに1つの状態異常を選択 (リストで渡されている場合)
            # 単一の文字列で渡された場合も random.choice はそのまま使える
            if isinstance(ailment_candidates, list):
                ailment = random.choice(ailment_candidates)
            else:
                ailment = ailment_candidates # 単一の文字列の場合
                
            # 状態異常の詳細データ（毒のダメージ量など）
            ailment_data = skill_effect.get('ailment_data', {})
            
            # --- 状態異常の適用処理 ---
            
            # 既に同じ状態異常にかかっているかチェック
            if ailment in self.status_effects:
                # 既存のdurationを更新
                self.status_effects[ailment]['duration'] = duration
            else:
                # 新しい状態異常の適用
                self.status_effects[ailment] = {
                    'duration': duration,
                    'type': 'ailment', # この情報があることで、バフ・デバフと区別しやすい
                    'data': ailment_data
                }

    # --- 新しいメソッド: ターン終了時の効果処理 ---
    def process_turn_end_effects(self):
        """
        ターン終了時に継続効果の処理、カウントダウン、解除を行う
        """
        logs = []
        expired_effects = []
        fainted_by_effect = False # 継続ダメージで戦闘不能になったか
        
        # 1. 効果の処理とカウントダウン
        for key, effect_data in list(self.status_effects.items()): # list()でコピーして反復中に変更できるようにする
            
            # --- A. 状態異常 (継続ダメージなど) の処理 ---
            if effect_data['type'] == 'ailment':
                ailment_type = key
                data = effect_data['data']
                
                if ailment_type == 'poison':
                    # 毒ダメージ計算 (ここでは最大HPの10%とし、データがあればそれを使う)
                    damage_percent = data.get('damage_percent', 0.1)
                    damage = max(1, int(self.max_hp * damage_percent))
                    
                    self.current_hp = max(0, self.current_hp - damage)
                    logs.append(f"💀 {self.name}は毒に侵され、{damage} のダメージを受けた！")
                
                elif ailment_type == 'burn':
                    # 火傷ダメージ計算 (固定値)
                    damage = data.get('damage', 5)
                    self.current_hp = max(0, self.current_hp - damage)
                    logs.append(f"🔥 {self.name}は火傷で、{damage} のダメージを受けた！")
                    
                # 継続ダメージで倒れたかチェック
                if self.current_hp <= 0:
                    self.is_alive = False
                    fainted_by_effect = True
                    logs.append(f"💥 {self.name}は継続ダメージにより力尽きた...")
            
            # --- B. 継続ターンを減らす ---
            effect_data['duration'] -= 1
            if effect_data['duration'] <= 0:
                expired_effects.append(key)
        
        # 2. 期限切れ効果の解除
        for key in expired_effects:
            # 継続ダメージで既に倒れている場合は、解除ログは不要
            if fainted_by_effect and self.status_effects[key]['type'] == 'ailment':
                del self.status_effects[key]
                continue

            effect_data = self.status_effects.pop(key)
            
            if effect_data['type'] in ['buff', 'debuff']:
                stat_key = key
                # original_valueに戻す (ベース値の参照方法を修正)
                # 注: ここでは一時的に変更した属性値を、記録しておいた元の値に戻します。
                
                # 記録しておいた元の値を再設定
                # keyが'physical_attack'などの属性名に対応していることが前提
                self.reset_status_to_base(stat_key, effect_data['original_value'])
                
                if effect_data['type'] == 'buff':
                    logs.append(f"⬇️ {self.name}の**{stat_key}**上昇効果が切れた。")
                else: # debuff
                    logs.append(f"⬆️ {self.name}の**{stat_key}**低下効果が治った。")
            
            elif effect_data['type'] == 'ailment':
                logs.append(f"✨ {self.name}の**{key}**状態が治った！")
        
        # 倒れたか、ログメッセージ、何か解除されたかを返す
        return logs, fainted_by_effect

    def apply_passive_effect(self, skill):
        """
        習得したパッシブスキルの効果をモンスター自身に適用する。
        適用結果のメッセージをリストで返す。
        """
        message = []
        
        # 物理攻撃
        if "physical_attack" in skill.effect.keys():
            amount = skill.effect["physical_attack"]
            self.physical_attack += amount
            self.base_physical_attack += amount 
            message.append(f"物理攻撃力 +{amount}")
            
        # 物理防御
        if "physical_defense" in skill.effect.keys():
            amount = skill.effect["physical_defense"]
            self.physical_defense += amount
            self.base_physical_defense += amount
            message.append(f"物理防御力 +{amount}")
            
        # 魔法攻撃
        if "magic_attack" in skill.effect.keys():
            amount = skill.effect["magic_attack"]
            self.magic_attack += amount
            self.base_magic_attack += amount
            message.append(f"魔法攻撃力 +{amount}")

        # 魔法防御
        if "magic_defense" in skill.effect.keys():
            amount = skill.effect["magic_defense"]
            self.magic_defense += amount
            self.base_magic_defense += amount
            message.append(f"魔法防御力 +{amount}")
            
        # 回避率
        if "dodge_rate" in skill.effect.keys():
            amount = skill.effect["dodge_rate"]
            self.dodge_rate += amount
            # UIで表示しやすいように%表示に変換
            message.append(f"回避率 +{int(amount * 100)}%")
            
        # すばやさ
        if "speed" in skill.effect.keys():
            amount = skill.effect["speed"]
            self.speed += amount
            message.append(f"すばやさ +{amount}")
            
        return message