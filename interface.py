# ==================================
# 1. バトル関連のI/O
# ==================================

def display_battle_start(enemy_name):
    """バトルの開始メッセージを表示"""
    print(f"野生の{enemy_name}が現れた！")
    print("--------------------")

def display_battle_status(current_monster, enemy):
    """戦闘中のステータスを表示"""
    print(f"敵: {enemy.name}")
    print(f"HP: [{enemy.get_hp_bar()}]")
    print("--------------------")

    print(f"プレイヤー: {current_monster.name}")
    print(f"HP: {current_monster.current_hp}/{current_monster.max_hp}")
    print(f"MP: {current_monster.current_mp}/{current_monster.max_mp}")
    print("--------------------")

def get_battle_command():
    """バトルのコマンド選択メニューを表示し、選択肢を返す"""
    print("コマンドを選択してください:")
    print("1. こうげき")
    print("2. スキル")
    print("3. ぼうぎょ")
    print("4. スカウト")
    print("5. いれかえ")
    print("6. にげる")
    return input("> ")

def display_skill_menu(active_skills):
    """スキル選択メニューを表示し、選択肢を返す"""
    if not active_skills:
        print("💡 習得しているアクティブスキルがありません。")
        return None, "skill_none"

    print("\n--- スキル選択 ---")
    for i, skill in enumerate(active_skills):
        print(f"[{i+1}] {skill.name} (消費MP: {skill.mp_cost})")
    print("0. 戻る")

    try:
        choice = int(input("> "))
        if choice == 0:
            return None, "skill_back"
        
        if 1 <= choice <= len(active_skills):
            selected_skill = active_skills[choice - 1]
            return selected_skill, "skill_selected"
        else:
            print("無効な選択です。")
            return None, "invalid"

    except ValueError:
        print("無効な入力です。数字を入力してください。")
        return None, "invalid"

# ==================================
# 2. メインメニュー/管理画面関連のI/O
# ==================================

def get_main_menu_choice():
    """メインメニューを表示し、選択肢を返す"""
    print("\n--- メインメニュー ---")
    print("1. フィールドへ出発 (バトル開始)")
    print("2. モンスター管理")
    print("3. ゲーム終了")
    return input("選択してください: ")

def get_management_menu_choice():
    """モンスター管理メニューを表示し、選択肢を返す"""
    print("\n--- モンスター管理 ---")
    print("1. ステータス確認")
    print("2. スキルツリー確認/習得")
    print("3. メインメニューに戻る")
    return input("選択してください: ")

def get_monster_selection(monsters, prompt="どのモンスターを選択しますか？", include_back=True):
    """モンスター一覧を表示し、選択を求める"""
    print("--- 所持モンスター ---")
    alive_monsters = [m for m in monsters if m.is_alive]
    if not alive_monsters:
        print("まだモンスターがいません。")
        return None

    for i, monster in enumerate(alive_monsters):
        print(f"[{i+1}] {monster.name} - Lvl{monster.level} HP:{monster.current_hp}/{monster.max_hp} {'(前衛)' if i == 0 else ''}")
    
    if include_back:
        print(f"0. 戻る")
    
    while True:
        try:
            choice = input(f"{prompt} (> )")
            if include_back and choice == '0':
                return "back"
                
            index = int(choice) - 1
            if 0 <= index < len(alive_monsters):
                return alive_monsters[index]
            else:
                print("無効な選択です。")
        except ValueError:
            print("無効な入力です。数字を入力してください。")