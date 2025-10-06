import random
import json # <- これを追加
import os # <- これを追加 (ファイルの読み込みに必要)
import sys # <- これを追加 (エラーハンドリングに必要)

class Battle:
    def __init__(self, player, enemy_monster):
        self.player = player
        self.current_monster = player.monsters[0] # 戦闘に出す最初のモンスター
        self.enemy = enemy_monster
        self.participated_monsters = {self.current_monster} # 戦闘に参加したモンスターのセット

        self.config = self._load_config()

        self._apply_passive_start_of_battle_effects() # 戦闘開始時のパッシブスキル効果を適用

    def _load_config(self):
        """
        battle_config.jsonから設定をロードする
        """
        base_path = os.path.dirname(os.path.abspath(__file__))
        data_path = os.path.join(base_path, 'data', 'battle_config.json')
        
        try:
            with open(data_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"Error: JSONファイル {data_path} が見つかりません。")
            sys.exit(1)
        except json.JSONDecodeError:
            print(f"Error: JSONファイル {data_path} のフォーマットが不正です。")
            sys.exit(1)

    def apply_skill_effect(self, user, skill):
        """
        アクティブスキルの効果を適用し、ログメッセージのリストを返す
        """
        target = self.enemy
        logs = []
        effect = skill.effect
        
        # スキル効果を適用
        if 'heal' in skill.effect:
            heal_amount = skill.effect.get('heal', 0)
            user.current_hp = min(user.max_hp, user.current_hp + heal_amount)
            logs.append(f"💚 {user.name}はHPを{heal_amount}回復した！") # 🔥 print()からlogs.append()に修正
            
        if 'damage_multiplier' in effect:
            multiplier = effect.get('damage_multiplier', 1.0)
            hits = effect.get('hits', 1)
            
            # 物理・魔法攻撃のどちらを参照するか決定
            damage_type = effect.get('damage_type')
            if damage_type == 'physical':
                base_attack = user.physical_attack
                enemy_defense = target.physical_defense
            elif damage_type == 'magic':
                base_attack = user.magic_attack
                enemy_defense = target.magic_defense
            else: # damage_typeの指定がない場合は物理をデフォルトとする
                base_attack = user.physical_attack
                enemy_defense = target.physical_defense
            
            total_damage_dealt = 0
            
            for i in range(hits):
                # ダメージ = (モンスター攻撃力 * 倍率) - 敵の防御力
                raw_damage = int(base_attack * multiplier) 
                
                # 防御力減算
                damage = max(1, raw_damage - enemy_defense)
                
                # 敵にダメージを適用
                target.current_hp = max(0, target.current_hp - damage)
                
                # ログ生成
                if hits > 1:
                    logs.append(f"💥 {target.name} に {damage} のダメージを与えた！ ({i+1}/{hits}ヒット)")
                else:
                    logs.append(f"💥 {target.name} に {damage} のダメージを与えた！")
                    
                total_damage_dealt += damage
                
                # 連続攻撃で敵が倒れたら中断
                if not target.is_alive:
                    break
            
            if hits > 1 and total_damage_dealt > 0 and target.is_alive:
                logs.append(f" (合計 {total_damage_dealt} ダメージ)") # 🔥 print()からlogs.append()に修正

            # パッシブスキル: 吸血 (ライフスティール)
            for passive_skill in user.get_passive_skills():
                if passive_skill.name == '吸血':
                    life_steal_ratio = passive_skill.effect.get('life_steal', 0.0)
                    life_steal_amount = int(total_damage_dealt * life_steal_ratio)
                    if life_steal_amount > 0:
                        user.current_hp = min(user.max_hp, user.current_hp + life_steal_amount)
                        logs.append(f"💉 {user.name}は{life_steal_amount}のHPを吸収して回復した！") # 🔥 print()からlogs.append()に修正
                    break 

        # その他の効果 (自傷、バフ/デバフ)
        if 'self_damage' in skill.effect:
            user.current_hp -= skill.effect['self_damage']
            logs.append(f"💔 {user.name}は {skill.effect['self_damage']} の反動ダメージを受けた！")

        if 'type' in skill.effect:
            
            if skill.effect.get('type') == 'buff':
                user.apply_buff_effect(skill.effect)
                logs.append(f"⬆️ {user.name}に強化効果がかかった！") 

            elif skill.effect.get('type') == 'debuff':
                target.apply_debuff_effect(skill.effect) 
                logs.append(f"⬇️ {target.name}に弱体効果がかかった！")
                
            elif skill.effect.get('type') == 'ailment':
                target.apply_ailment_effect(skill.effect)
                logs.append(f"⚠️ {target.name}に状態異常が付与された！")
            
        return logs
    
    def _apply_passive_start_of_battle_effects(self):
        """
        バトル開始時に発動するパッシブスキルを処理する (例: リーダーシップ)
        """
        for monster in self.player.monsters:
            for skill in monster.get_passive_skills():
                if skill.name == 'リーダーシップ':
                    self._apply_leadership_buff(monster, skill)
                    
    def _apply_leadership_buff(self, leader_monster, leadership_skill):
        """
        リーダーシップスキルを発動し、味方にバフをかける
        """
        effect = leadership_skill.effect
        if effect.get("buff") == "ally":
            print(f"🚩 {leader_monster.name}のリーダーシップが発動！")
            
            # 全ての生存している味方（リーダー自身を含む）にバフを適用
            for ally in self.player.monsters:
                if ally.is_alive:
                    # Monster.pyの既存のメソッドを呼び出す
                    ally.apply_buff_effect(effect)

    def _process_passive_extra_attack(self, attacker):
        """
        連携攻撃などのパッシブスキルによる追加攻撃を処理する
        """
        for skill in attacker.get_passive_skills():
            if skill.name == '連携攻撃':
                chance = skill.effect.get("extra_attack_chance", 0.0)
                if random.random() < chance:
                    # 追加攻撃の発動
                    print(f"🔄 {attacker.name}の連携攻撃が発動！")
                    # シンプルな物理攻撃を再実行
                    extra_damage = max(1, attacker.physical_attack - self.enemy.physical_defense)
                    self.enemy.take_damage(extra_damage)
                    # 追加攻撃で敵が倒れたかチェック
                    if self.enemy.is_fainted():
                        return "enemy_fainted" # 敵が倒れたことを示す
                    return "extra_attack_used" # 追加攻撃を実行したことを示す

    def process_attack(self):
        """
        「こうげき」コマンドを実行する
        """
        current = self.current_monster
        enemy = self.enemy
        logs = []

        damage = max(1, current.physical_attack - enemy.physical_defense // 2)
        
        # 敵の回避判定
        if random.random() < enemy.dodge_rate:
            logs.append(f"💨 {enemy.name}は {current.name} の攻撃を華麗に避けた！")
        else:
            enemy.current_hp = max(0, enemy.current_hp - damage)
            logs.append(f"💥 {current.name}は {enemy.name} に {damage} のダメージを与えた！")

        return logs, self.check_battle_status() # ログとバトルの結果を返す

    def process_guard(self):
        """
        「ぼうぎょ」コマンドを実行する (防御フラグを立てる)
        """
        self.current_monster.is_guarding = True # Monsterクラスにこの属性が必要です
        return [f"🛡️ {self.current_monster.name}は身構えた。次のターンの被ダメージが減少する。"]

    def process_escape(self):
        """
        「にげる」コマンドを実行する
        """
        escape_rate = 0.5 # 逃走成功率
        if random.random() < escape_rate:
            return ["🏃‍♂️ 戦闘から離脱しました。"], "escape"
        else:
            return ["🛑 逃走に失敗した！"], None
        
# --- ターンの進行とチェック ---

    def process_enemy_turn(self):
        """
        敵の行動を実行する (シンプルな攻撃のみ)
        """
        current = self.current_monster
        enemy = self.enemy
        logs = []
        
        # 敵の攻撃ロジック
        damage = max(1, enemy.physical_attack - current.physical_defense // 2)
        
        # 防御状態の確認
        if current.is_guarding:
            damage = max(1, damage // 2)
            current.is_guarding = False # 防御状態を解除
            
        # プレイヤーモンスターの回避判定 (ここではシンプルに実装)
        if random.random() < current.dodge_rate:
            logs.append(f"💨 {current.name}は {enemy.name} の攻撃を華麗に避けた！")
        else:
            current.current_hp = max(0, current.current_hp - damage)
            logs.append(f"💥 {enemy.name}は {current.name} に {damage} のダメージを与えた！")

        return logs, self.check_battle_status()
    
    def check_battle_status(self):
        """
        バトルの勝敗をチェックする
        """
        if self.enemy.current_hp <= 0:
            return "win"
        
        # プレイヤー側の全滅判定（ここではcurrent_monsterのみチェック）
        # 厳密にはplayer.monsters全体をチェックすべきだが、一旦current_monsterのみで
        if self.current_monster.current_hp <= 0:
            # 交代可能なモンスターがいるかチェック
            if any(m.is_alive and m != self.current_monster for m in self.player.monsters):
                return "switch_needed"
            else:
                return "lose"
        
        return None # バトル継続
    
    def process_switch(self, new_monster):
        """
        戦闘中のモンスターを新しいモンスターに交代させる
        :param new_monster: 交代させる新しいMonsterオブジェクト
        :return: ログメッセージのリスト
        """
        logs = []
        old_monster = self.current_monster
        
        # 既にapp.py側でチェックされているはずだが、念のため生存チェック
        if not new_monster.is_alive:
            return ["💀 そのモンスターは戦闘不能です。交代できません。"]
            
        # 交代の実行
        self.current_monster = new_monster
        self.participated_monsters.add(new_monster)
        
        # ログメッセージ
        logs.append(f"🔄 {old_monster.name}を引っ込めた！")
        logs.append(f"🔥 {new_monster.name}が戦闘に飛び出した！")
        
        return logs
    
    def process_scout(self):
        """
        スカウトコマンドを実行し、成否を判定する。
        :return: ログメッセージのリスト, バトル結果 ('scout_success' または None)
        """
        logs = []
        enemy = self.enemy
        
        # 1. 成功率の計算
        # 敵のHPが低いほど成功率が上がる (例: (max_hp - current_hp) / max_hp)
        hp_ratio = (enemy.max_hp - enemy.current_hp) / enemy.max_hp
        
        # 基礎スカウト率とHP補正を組み合わせる
        # (enemy.scout_rateは0.05〜0.2を想定)
        final_rate = enemy.scout_rate * (1 + hp_ratio * 1.5) # HP補正は最大で1.5倍まで影響
        final_rate = min(1.0, final_rate) # 最大100%

        # 2. 判定
        if random.random() < final_rate:
            # 成功
            logs.append(f"🎉 スカウト成功！野生の**{enemy.name}**は仲間になりたそうにこちらを見ている！")
            return logs, "scout_success"
        else:
            # 失敗
            logs.append(f"💔 スカウト失敗... {enemy.name}は警戒しているようだ。")
            return logs, None
        
    def get_available_active_skills(self):
        """
        現在使用可能なアクティブスキルと消費MPをリストで返す
        """
        return [
            skill for skill in self.current_monster.get_active_skills()
            if self.current_monster.current_mp >= skill.mp_cost
        ]

    def process_skill_use(self, selected_skill):
        """
        選択されたスキルを使用する処理
        """
        current = self.current_monster
        logs = []
        
        if current.current_mp < selected_skill.mp_cost:
            logs.append(f"❌ MPが足りません。（必要MP: {selected_skill.mp_cost}）")
            return logs, None # ターンを消費しない

        # MP消費と初期ログ
        current.current_mp -= selected_skill.mp_cost
        logs.append(f"✨ {current.name}は {selected_skill.name} を使った！ (MP-{selected_skill.mp_cost})")

        # スキル効果の適用とログの取得
        effect_logs = self.apply_skill_effect(current, selected_skill)
        logs.extend(effect_logs) # スキル効果で発生したログを結合する
        
        result = self.check_battle_status() 
        
        # 連携攻撃などのパッシブスキルチェック (スキル使用後)
        if result != 'win':
            passive_result = self._process_passive_extra_attack(current)
            if passive_result == "enemy_fainted":
                result = 'win' # パッシブで敵が倒れた場合
        
        return logs, result
    
    def process_turn_end_effects(self):
        """
        ターン終了時、プレイヤーと敵の継続効果を処理する。
        継続ダメージによる勝敗判定を行う。
        :return: ログメッセージのリスト, バトル結果 ('win', 'lose', 'switch_needed', or None)
        """
        logs = []
        
        # --- 1. 敵モンスターの継続効果処理 ---
        # logs_enemy: 継続ダメージや効果解除のメッセージ
        # fainted_enemy: 継続ダメージで敵が倒れたか
        logs_enemy, fainted_enemy = self.enemy.process_turn_end_effects()
        logs.extend(logs_enemy)
        
        # 継続ダメージで敵が倒れた場合
        if fainted_enemy:
            return logs, "win"
            
        # --- 2. プレイヤーモンスターの継続効果処理 ---
        logs_player, fainted_player = self.current_monster.process_turn_end_effects()
        logs.extend(logs_player)
        
        # 継続ダメージでプレイヤーモンスターが倒れた場合
        if fainted_player:
            # 交代可能なモンスターがいるかチェック
            if any(m.is_alive for m in self.player.monsters if m != self.current_monster):
                return logs, "switch_needed"
            else:
                return logs, "lose"
        
        # --- 3. その他のターン終了時処理 ---
        
        # (防御フラグなどのリセットは、各処理やMonster.py側で個々に行うのが望ましい)

        return logs, None # バトル継続