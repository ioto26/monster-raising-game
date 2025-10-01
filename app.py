# app.py

import streamlit as st
import random
# Monster, Battle, Playerは別途インポートされているものと仮定します
from Monster import Monster 
from Battle import Battle
from Player import Player

st.set_page_config(page_title="モンスター育成ゲーム", layout="wide")
st.title("⚔️ モンスター育成ゲーム 📱")

# --- 1. 初期化とセッションステートの管理 ---
if 'player' not in st.session_state:
    # ゲーム開始時の初期化処理
    player = Player("主人公")

    player.add_monster(Monster.from_json("スライム"))
    player.add_monster(Monster.from_json("オオカミ"))

    st.session_state.player = player
    st.session_state.game_state = 'main_menu' # 現在のゲーム状態を保持
    st.session_state.battle = None # バトルオブジェクト
    st.session_state.battle_log = [] # ログ表示用リスト

    st.session_state.battle_state = 'player_turn' # 新しいバトルの詳細状態
    st.session_state.player_action = None # 選択されたコマンド
    st.session_state.turn_message = None # ターン処理後のメッセージ

if 'management_state' not in st.session_state:
    st.session_state.management_state = 'menu'
if 'selected_monster' not in st.session_state:
    st.session_state.selected_monster = None

# --- 2. メインメニューの関数 ---
def main_menu():
    st.header("--- メインメニュー ---")
    st.write(f"所持金: {st.session_state.player.gold}G")

    col1, col2, col3 = st.columns(3)
    
    # 1. フィールドへ出発 (バトル開始)
    with col1:
        if st.button("1. フィールドへ出発 (バトル開始)", key="start_battle_btn"):
            st.session_state.game_state = 'battle_setup'
            st.rerun() # 状態変更後、再描画を強制

    # 2. モンスター管理
    with col2:
        if st.button("2. モンスター管理", key="manage_monsters_btn"):
            st.session_state.game_state = 'management_menu'
            st.rerun()

    # 3. ゲーム終了
    with col3:
        if st.button("3. ゲーム終了", key="exit_game_btn"):
            st.success("👋 冒険を終えました。またね！")
            st.stop()

# --- 3. バトル準備の関数 (start_battle_loop の前半部分) ---
def battle_setup():
    player = st.session_state.player
    
    # 敵モンスターの生成とステータス調整ロジックを移植
    enemy_type = random.choice(["ゴブリン", "コウモリ", "オオカミ"])
    
    enemy_monster = Monster.from_json(enemy_type)

    enemy_monster.max_hp = int(enemy_monster.max_hp * random.uniform(0.8, 1.2))
    enemy_monster.current_hp = enemy_monster.max_hp
    enemy_monster.max_mp = int(enemy_monster.max_mp * random.uniform(0.8, 1.2))
    enemy_monster.current_mp = enemy_monster.max_mp
    enemy_monster.physical_attack = int(enemy_monster.physical_attack * random.uniform(0.8, 1.2))
    enemy_monster.physical_defense = int(enemy_monster.physical_defense * random.uniform(0.8, 1.2))
    enemy_monster.magic_attack = int(enemy_monster.magic_attack * random.uniform(0.8, 1.2))
    enemy_monster.magic_defense = int(enemy_monster.magic_defense * random.uniform(0.8, 1.2))
    enemy_monster.speed = int(enemy_monster.speed * random.uniform(0.8, 1.2))
    enemy_monster.level = random.randint(1, 3)  # 敵のレベルを1から3の間でランダムに設定
    enemy_monster.enemy_exp = int(enemy_monster.enemy_exp * (1 + enemy_monster.level * 0.1))
    enemy_monster.enemy_gold = int(enemy_monster.enemy_gold * (1 + enemy_monster.level * 0.1))
    enemy_monster.scout_rate = enemy_monster.scout_rate * (1 - enemy_monster.level * 0.05)

    # バトルオブジェクトをセッションに保存し、バトル開始状態へ移行
    st.session_state.battle = Battle(player, enemy_monster)
    st.session_state.game_state = 'in_battle'
    st.session_state.battle_log = [f"野生の{enemy_monster.name}が現れた！"]
    st.rerun()

# --- 4. モンスター管理メニューの関数 (Placeholder) ---
def management_menu():
    st.header("--- モンスター管理 ---")
    player = st.session_state.player

    # --- ステータス確認/スキル習得のメインメニュー ---
    if st.session_state.management_state == 'menu':
        st.subheader("管理メニューを選択してください:")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("1. ステータス確認", key="manage_status"):
                st.session_state.management_state = 'select_monster_for_status'
                st.rerun()
        with col2:
            if st.button("2. スキルツリー確認/習得", key="manage_skill"):
                st.session_state.management_state = 'select_monster_for_skill'
                st.rerun()
                
        st.markdown("---")
        if st.button("メインメニューに戻る", key="management_back_btn"):
            st.session_state.game_state = 'main_menu'
            st.session_state.management_state = 'menu' # 状態をリセット
            st.rerun()

    # --- モンスター選択画面 ---
    elif st.session_state.management_state.startswith('select_monster'):
        
        st.subheader("どのモンスターを管理しますか？")
        
        # モンスターリストの表示と選択
        monster_options = [
            f"[{i+1}] {m.name} (Lv.{m.level} HP:{m.current_hp}/{m.max_hp})" 
            for i, m in enumerate(player.monsters)
        ]
        
        selected_monster_display = st.selectbox(
            "モンスターを選択", 
            monster_options, 
            key="monster_select_box"
        )
        
        # 選択されたモンスターオブジェクトを取得し、セッションに保存
        selected_index = monster_options.index(selected_monster_display)
        selected_monster = player.monsters[selected_index]
        st.session_state.selected_monster = selected_monster

        # アクションボタン
        is_status_check = st.session_state.management_state == 'select_monster_for_status'
        action_label = "ステータス確認へ" if is_status_check else "スキル習得へ"
        next_state = "view_status" if is_status_check else "learn_skill_tree_select"

        col_next, col_back = st.columns(2)
        with col_next:
            if st.button(f"✅ {action_label}", key="confirm_monster_select"):
                st.session_state.management_state = next_state
                st.rerun()
        with col_back:
            if st.button("↩️ 戻る", key="monster_select_back"):
                st.session_state.management_state = 'menu'
                st.rerun()
            
        st.markdown("---")
            
    # --- 3. ステータス表示 ---
    elif st.session_state.management_state == 'view_status':
        # 選択したモンスターのステータスを表示
        view_status_gui(st.session_state.selected_monster)
        if st.button("↩️ 戻る", key="status_back"):
            st.session_state.management_state = 'menu'
            st.rerun()

    # --- 4. スキル習得の処理 ---
    elif st.session_state.management_state == 'learn_skill_tree_select':
        # スキル習得ロジックへ
        learn_skill_gui(st.session_state.selected_monster)

# --- 5. バトルループの関数 (最も複雑な部分) ---
def battle_loop():
    if st.session_state.game_state != 'in_battle':
        return
        
    # battle_setup()で必ずin_battleに遷移するため、Noneチェックはほぼ不要だが念のため
    if st.session_state.battle is None:
        return
    
    battle = st.session_state.battle
    
    # 敗北判定などでメインメニューに戻る前に処理を終了
    if st.session_state.game_state != 'in_battle':
        return
    
    # --- 1. ステータス表示エリア (常に最上位に固定) ---
    st.header("💥 バトル中 💥")
    
    # 敵のステータス表示 (HPバーのみ、数値非表示)
    st.subheader(f"敵: {battle.enemy.name}")
    enemy_hp_ratio = battle.enemy.current_hp / battle.enemy.max_hp
    # 具体的な数値は表示せず、名前とバーのみ
    st.progress(max(0.0, enemy_hp_ratio), text="HP") 
    
    # プレイヤーのステータス表示 (HP, MP数値あり)
    st.subheader(f"プレイヤー: {battle.current_monster.name}")
    player_hp_ratio = battle.current_monster.current_hp / battle.current_monster.max_hp
    st.progress(max(0.0, player_hp_ratio), text=f"HP: {battle.current_monster.current_hp}/{battle.current_monster.max_hp}")
    st.caption(f"MP: {battle.current_monster.current_mp}/{battle.current_monster.max_mp}")
    
    st.markdown("---")
    
    # --- 2. ターンの進行処理 (状態に応じてロジックを実行) ---
    
    # バトル終了チェック
    if st.session_state.battle_state in ['win', 'lose', 'escape']:
        battle_end_screen()
        return

    # プレイヤーのターン
    if st.session_state.battle_state == 'player_turn':
        # コマンド選択エリアをログの上に配置する
        player_turn_gui(battle)
        
        # ログ表示エリアをコマンドの下に配置する
        st.markdown("---")
        st.subheader("📝 バトルログ")
        for log in st.session_state.battle_log[-10:]:
            st.code(log)
        st.markdown("---")
    
    # 敵のターン実行
    elif st.session_state.battle_state == 'enemy_turn':
        # 1. 敵の行動を実行
        logs, result = battle.process_enemy_turn()
        st.session_state.battle_log.extend(logs)
        
        # 敵の行動後に勝敗をチェックし、バトル終了なら再描画
        if result is not None:
            st.session_state.battle_state = result
            st.rerun() # 勝利/敗北/強制交代画面へ
            return

        # ---------------------------------------------
        # 2. ターン終了時の継続効果を処理 (🔥 ここを追加 🔥)
        # ---------------------------------------------
        # 継続ダメージ、バフ・デバフのカウントダウンなどを処理
        effect_logs, effect_result = battle.process_turn_end_effects() 
        st.session_state.battle_log.extend(effect_logs)
        
        # 継続ダメージ等で勝敗が決した場合をチェック
        if effect_result is not None:
            st.session_state.battle_state = effect_result
            st.rerun() # 勝利/敗北/強制交代画面へ
            return

        # 3. 問題なければ次のプレイヤーのターンへ
        st.session_state.battle_state = 'player_turn'
            
        # 処理が実行され、ログが更新されたので画面を更新
        st.rerun()
        
    # モンスター入れ替えが必要な場合
    elif st.session_state.battle_state == 'switch_needed':
        
        # 交代可能なモンスターがいるかチェック (自分以外の生存モンスター)
        alive_others = [m for m in battle.player.monsters if m.is_alive and m != battle.current_monster]
        
        if len(alive_others) > 0:
            # 強制交代画面へ遷移
            st.warning(f"⚠️ {battle.current_monster.name}は戦闘不能になりました！次のモンスターを選択してください。")
            st.session_state.battle_state = 'forced_switching' 
        else:
            # 交代可能なモンスターがいない場合は敗北
            st.session_state.battle_state = 'lose'
            
        st.rerun() # 状態変更後に再描画
        
    # 🔄 強制交代画面
    elif st.session_state.battle_state == 'forced_switching':
        # 強制交代UIを表示し、必ず交代させる
        switch_monster_gui(battle, is_forced=True)

    elif st.session_state.battle_state == 'skill_selection':
        skill_selection_gui(battle)

    elif st.session_state.battle_state == 'scout_success':
        scout_success_screen(battle)
        return
        
    # 任意交代画面 (コマンド選択時)
    elif st.session_state.battle_state == 'switching_monster':
        switch_monster_gui(battle, is_forced=False)


# --- 3. プレイヤーコマンド選択UI (新しいヘルパー関数) ---

def player_turn_gui(battle):
    st.subheader("コマンドを選択してください:")
    col1, col2, col3, col4, col5, col6 = st.columns(6)
    
    # 1. こうげき
    if col1.button("1. こうげき"):
        logs, result = battle.process_attack()
        st.session_state.battle_log.extend(logs)
        
        if result: # 勝敗が決した場合
            st.session_state.battle_state = result
        else:
            st.session_state.battle_state = 'enemy_turn' # 次は敵のターン
        st.rerun()
    
    # 2. スキル
    battle_monster = battle.current_monster
    active_skills = battle_monster.get_active_skills()
    
    # 覚えているスキルがない場合はボタンを無効化
    if col2.button("2. スキル", disabled=not active_skills):
        if active_skills:
            st.session_state.battle_state = 'skill_selection'
        else:
            st.session_state.battle_log.append("💡 習得しているアクティブスキルがありません。")
            
        st.rerun()
    
    # 3. ぼうぎょ
    if col3.button("3. ぼうぎょ"):
        logs = battle.process_guard()
        st.session_state.battle_log.extend(logs)
        st.session_state.battle_state = 'enemy_turn'
        st.rerun()

    # 4. スカウト (TODO: 確率判定を伴うため次ステップ)
    if col4.button("4. スカウト"):
        logs, result = battle.process_scout()
        st.session_state.battle_log.extend(logs)
        
        if result == "scout_success":
            # 成功した場合、スカウト成功状態へ遷移
            st.session_state.battle_state = 'scout_success'
        else:
            # 失敗した場合、敵のターンへ移行
            st.session_state.battle_state = 'enemy_turn'
            
        st.rerun()
        
    # 5. いれかえ (TODO: 選択肢を伴うため次ステップ)
    alive_others = [m for m in battle.player.monsters if m.is_alive and m != battle.current_monster]
    can_switch = len(alive_others) > 0
    
    if col5.button("5. いれかえ", disabled=not can_switch):
        if can_switch:
            # 交代可能なモンスターがいる場合、状態を遷移させる
            st.session_state.battle_state = 'switching_monster'
        else:
            st.session_state.battle_log.append("⚠️ 入れ替えられるモンスターがいません。")
            
        st.rerun()
        
    # 6. にげる
    if col6.button("6. にげる"):
        logs, result = battle.process_escape()
        st.session_state.battle_log.extend(logs)
        if result == "escape":
            st.session_state.battle_state = 'escape'
        else:
            st.session_state.battle_state = 'enemy_turn'
        st.rerun()
        
        
def battle_end_screen():
    result = st.session_state.battle_state
    battle = st.session_state.battle # Battleオブジェクトを取得

    # --- 1. 結果表示 ---
    if result == 'win':
        st.success("🎉 勝利！")
        
        # --- 2. 経験値、ゴールド獲得処理 ---
        
        gained_exp = battle.enemy.enemy_exp
        gained_gold = battle.enemy.enemy_gold
        
        # ゴールド獲得 (Player.pyのメソッドを使用)
        st.session_state.player.gain_gold(gained_gold) # Player.pyで処理
        st.info(f"💰 **{gained_gold}G** を獲得しました！ (所持金: {st.session_state.player.gold}G)")
        
        st.markdown("---")
        st.subheader("経験値とレベルアップ")
        
        # 経験値獲得とレベルアップ処理 (全モンスターを対象に)
        for monster in st.session_state.player.monsters:
            # 獲得前のレベルを記録
            old_level = monster.level
            
            # 経験値獲得 (Monster.pyのgain_experienceがレベルアップを自動処理)
            monster.gain_experience(gained_exp)
            
            # レベルアップしたかチェック
            if monster.level > old_level:
                st.balloons() # レベルアップ時にバルーンを出す
                st.success(f"🎉 **{monster.name}** は **Lv.{old_level}** から **Lv.{monster.level}** にレベルアップしました！")
            else:
                st.write(f"✨ **{monster.name}** は **{gained_exp}** の経験値を獲得しました！ (残り: {monster.experience}/{monster.get_next_level_exp()})")
        
        # -----------------------------

    elif result == 'lose':
        st.error("😭 敗北...")
    elif result == 'escape':
        st.info("🏃‍♂️ 逃走成功！")
        
    st.markdown("---")
    
    # --- 3. メインメニューに戻るボタン (状態リセットはボタン内へ) ---
    if st.button("メインメニューに戻る", key="battle_end_back_btn"):
        # バトルオブジェクトと状態のリセットをボタン内で行う
        st.session_state.battle = None 
        st.session_state.battle_state = 'player_turn' # 次のバトル用に初期値に戻す
        
        st.session_state.game_state = 'main_menu'
        st.session_state.battle_log = []
        st.rerun()

def view_status_gui(monster):
    st.subheader(f"--- {monster.name}のステータス ---")
    
    col_level, col_exp = st.columns(2)
    col_level.write(f"**レベル**: {monster.level}")
    col_exp.write(f"**経験値**: {monster.experience}/{monster.get_next_level_exp()}")
    
    st.write(f"**HP**: {monster.current_hp}/{monster.max_hp}")
    st.progress(monster.current_hp / monster.max_hp, text="HP")
    st.write(f"**MP**: {monster.current_mp}/{monster.max_mp}")
    
    st.write(f"**スキルポイント**: {monster.skill_points} SP")
    st.markdown("---")
    
    # 3カラムで詳細ステータスを表示
    col_atk, col_def, col_magic = st.columns(3)
    col_speed, col_dodge, col_dummy = st.columns(3)
    
    col_atk.metric("物理攻撃", monster.physical_attack)
    col_def.metric("物理防御", monster.physical_defense)
    col_magic.metric("魔法攻撃", monster.magic_attack)
    col_speed.metric("魔法防御", monster.magic_defense)
    col_dodge.metric("すばやさ", monster.speed)
    col_dummy.metric("回避率", f"{int(monster.dodge_rate * 100)}%")

    st.markdown("---")

    # スキルの表示
    active_skills = monster.get_active_skills()
    passive_skills = monster.get_passive_skills()

    with st.expander("▶️ アクティブスキル一覧"):
        if active_skills:
            for skill in active_skills:
                st.write(f"- **{skill.name}** (MP{skill.mp_cost}): {skill.description}")
        else:
            st.write("なし")

    with st.expander("🛡️ パッシブスキル一覧"):
        if passive_skills:
            for skill in passive_skills:
                st.write(f"- **{skill.name}**: {skill.description}")
        else:
            st.write("なし")

def learn_skill_gui(monster):
    if not monster.skill_trees:
        st.warning(f"{monster.name} にはスキルツリーがありません。")
    else:
        st.subheader(f"--- {monster.name} のスキル習得 ---")
        st.info(f"残りスキルポイント: **{monster.skill_points} SP**")

        # スキルツリーの選択 (現在は単一を想定)
        tree_names = [tree.name for tree in monster.skill_trees]
        selected_tree_name = st.selectbox("どのスキルツリーに割り振りますか？", tree_names, key="skill_tree_select_box")
        selected_tree = next((t for t in monster.skill_trees if t.name == selected_tree_name), None)

        if selected_tree:
            st.markdown("---")
            st.caption(f"🌳 **{selected_tree.name} ツリー**")
            
            # 習得可能スキルを取得
            learnable_skills = [node.skill for node in selected_tree.nodes.values() 
                                if not node.skill.unlocked and all(prereq.skill.unlocked for prereq in selected_tree.nodes[node.skill.name].prerequisites)]

            if not learnable_skills:
                st.warning("習得できるスキルがありません。")
            else:
                st.caption("--- 習得可能スキル ---")
                
                skill_options = [f"SP{s.sp_cost}: {s.name} ({s.description})" for s in learnable_skills]
                selected_skill_display = st.selectbox("習得したいスキルを選択してください", skill_options, key="skill_learn_select")
                
                selected_skill_name = selected_skill_display.split(': ')[1].split(' (')[0]
                selected_skill = next((s for s in learnable_skills if s.name == selected_skill_name), None)
                
                if selected_skill:
                    st.write(f"**消費SP**: {selected_skill.sp_cost}")
                    
                    can_learn = monster.skill_points >= selected_skill.sp_cost
                    
                    if st.button(f"✨ {selected_skill.name} を習得する", key="learn_skill_button", disabled=not can_learn):
                        
                        # SkillTree.learn_skill() の呼び出し
                        points_spent = selected_tree.learn_skill(selected_skill.name, monster.skill_points)
                        
                        if points_spent is not None:
                            monster.skill_points -= points_spent
                            
                            # パッシブスキルの効果を適用し、スキルリストに追加
                            monster.skills.append(selected_skill) 
                            if selected_skill.category == 'passive':
                                stat_messages = monster.apply_passive_effect(selected_skill)

                                if stat_messages:
                                    st.info(f"**{monster.name}** のステータスが上昇しました: {', '.join(stat_messages)}")
                            
                            st.success(f"🎉 **{selected_skill.name}** を習得しました！スキルポイントを {points_spent} 消費しました。")
                            st.session_state.player = st.session_state.player # 状態更新を確実に
                            st.rerun()
                        else:
                            st.error("習得できませんでした。SPまたは前提スキルが不足しています。")
                    
                    if not can_learn:
                        st.error("スキルポイントが不足しています。")
            
    if st.button("↩️ 戻る", key="skill_back_to_menu"):
        st.session_state.management_state = 'menu'
        st.rerun()

def switch_monster_gui(battle, is_forced=False):
    st.subheader("どのモンスターと入れ替えますか？")
    player = battle.player
    current = battle.current_monster
    
    # 交代可能なモンスターを取得 (生存していて、現在のモンスターではない)
    switchable_monsters = [
        m for m in player.monsters 
        if m.is_alive and m != current
    ]

    # UI表示用のオプションリストを作成
    monster_options = [
        f"{m.name} (Lv.{m.level} HP:{m.current_hp}/{m.max_hp})"
        for m in switchable_monsters
    ]
    
    # 選択肢の先頭に「戻る」オプションを追加 (強制交代の場合は追加しない)
    if not is_forced:
        monster_options.insert(0, "↩️ コマンド選択に戻る")
    else:
        # 強制交代の場合は、選択肢がないとエラーになるため、ここでチェック
        if not monster_options:
            # このルートに来ることは稀だが、念のため
            st.session_state.battle_state = 'lose'
            st.error("エラー：交代可能なモンスターがいません。")
            st.rerun()
            return
    
    # モンスター選択
    selected_display = st.selectbox(
        "控えモンスターを選択",
        monster_options,
        # キーを動的にすることで強制/任意でウィジェットがリセットされるのを防ぐ
        key=f"switch_select_{'forced' if is_forced else 'normal'}"
    )

    # 戻るボタンの処理 (強制交代ではない場合のみ)
    if not is_forced and selected_display == "↩️ コマンド選択に戻る":
        if st.button("キャンセルしてコマンド選択に戻る"):
            st.session_state.battle_state = 'player_turn'
            st.session_state.battle_log.append("入れ替えをキャンセルしました。")
            st.rerun()
        return
        
    # 交代確定ボタンの処理
    
    # 選択されたモンスターオブジェクトを特定
    selected_name = selected_display.split(' (')[0]
    new_monster = next((m for m in switchable_monsters if m.name == selected_name), None)
    
    if new_monster and st.button(f"🔥 {new_monster.name}と交代！", key="confirm_switch_btn"):
        
        # Battle.py のメソッドを呼び出し、交代処理を実行
        logs = battle.process_switch(new_monster)
        st.session_state.battle_log.extend(logs)
        
        # 交代はターン消費アクションであり、敵のターンへ移行
        st.session_state.battle_state = 'enemy_turn'
        st.rerun()
        
    if is_forced:
        st.error("⚠️ 戦闘不能のため、交代をキャンセルすることはできません。必ずモンスターを選択してください。")

def scout_success_screen(battle):
    st.success(f"🎊 {battle.enemy.name}を仲間にしました！")
    
    # 敵モンスターオブジェクトをプレイヤーのモンスターリストに追加
    player = st.session_state.player
    enemy = battle.enemy
    
    # NOTE: バトル中の敵は、戦闘不能フラグなど立っていないクリーンな状態で追加するのが望ましい
    # 敵モンスターは、自身のHP/MPを全回復させてからプレイヤーに追加する
    enemy.current_hp = enemy.max_hp
    enemy.current_mp = enemy.max_mp
    enemy.is_alive = True
    
    # プレイヤーのリストに追加
    player.add_monster(enemy) # Player.pyのadd_monsterメソッドがログを出す (GUIでは無視されるが、安全のため)
    st.session_state.player = player # セッションステートを更新
    
    st.write(f"🎉 **{enemy.name}** があなたの仲間になりました！")
    
    # バトル終了処理
    if st.button("メインメニューに戻る", key="scout_end_back_btn"):
        # 🔥 バトルオブジェクトと状態のリセットをボタン内で行う
        st.session_state.battle = None 
        st.session_state.battle_state = 'player_turn' # 次のバトル用に初期値に戻す
        
        st.session_state.game_state = 'main_menu'
        st.session_state.battle_log = []
        st.rerun()

def skill_selection_gui(battle):
    st.subheader(f"{battle.current_monster.name} のスキルを選択してください:")
    
    # 使用可能なスキルを取得 (MPが足りないスキルも表示はする)
    all_active_skills = battle.current_monster.get_active_skills()
    available_skills = battle.get_available_active_skills()
    
    col1, col2 = st.columns([3, 1])

    # 1. スキルリスト表示と実行ボタン
    if all_active_skills:
        
        for i, skill in enumerate(all_active_skills):
            is_available = skill in available_skills
            
            # スキルの詳細を表示
            description = f"{skill.description} (MP: {skill.mp_cost})"
            
            # 実行ボタン
            button_label = f"✨ {skill.name}"
            
            if is_available:
                if col1.button(button_label, key=f"skill_use_{i}"):
                    # スキル使用処理を実行
                    logs, result = battle.process_skill_use(skill)
                    st.session_state.battle_log.extend(logs)
                    
                    if result: # 勝敗が決した場合
                        st.session_state.battle_state = result
                    else:
                        st.session_state.battle_state = 'enemy_turn' # 敵のターンへ
                    st.rerun()
            else:
                # MP不足などで使用不可の場合
                col1.button(button_label, disabled=True, key=f"skill_disabled_{i}", help="MPが足りません")

            col2.caption(description)
            
    else:
        st.info("習得しているアクティブスキルがありません。")

    st.markdown("---")
    
    # 2. 戻るボタン
    if st.button("↩️ コマンド選択に戻る", key="skill_back_btn"):
        st.session_state.battle_state = 'player_turn'
        st.session_state.battle_log.append("スキル選択をキャンセルしました。")
        st.rerun()

# --- 6. メインロジック（状態遷移）---
# この部分が、元の main() 関数の while ループの役割を果たします。
if st.session_state.game_state == 'main_menu':
    main_menu()
elif st.session_state.game_state == 'battle_setup':
    battle_setup()
elif st.session_state.game_state == 'in_battle':
    battle_loop()
elif st.session_state.game_state == 'management_menu':
    management_menu()
# ... (他の状態を追加)