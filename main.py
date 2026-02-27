import flet as ft
from datetime import datetime
import logging

# --- CẤU HÌNH ---
logging.basicConfig(level=logging.INFO)

DEF_BET = 10
PLAYERS_DEF = ["Người 1", "Người 2", "Người 3", "Người 4"]

# Bảng màu (Phẳng - An toàn cho mọi màn hình)
COLOR_BG = "#F5F7F9"
COLOR_HEADER_BG = "#FFFFFF"
COLOR_GOLD = "#F1C40F"

def main(page: ft.Page):
    # 1. CẤU HÌNH PAGE
    page.title = "TÁ LẢ PRO"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.bgcolor = COLOR_BG
    page.padding = ft.padding.only(top=60, left=15, right=15, bottom=20)
    page.horizontal_alignment = ft.CrossAxisAlignment.START 
    page.scroll = None 
    
    # 2. XỬ LÝ NÚT BACK (VUỐT CẠNH MÀN HÌNH)
    def view_pop(view):
        page.views.pop() 
        top_view = page.views[-1] 
        page.go(top_view.route) 
    
    page.on_view_pop = view_pop

    # --- BIẾN TOÀN CỤC ---
    state = {
        "bet": DEF_BET,
        "pot": 0,
        "players": [{"name": n, "money": 0} for n in PLAYERS_DEF],
        "history": [],      
        "current_logs": [],
        # MỚI: Tracking lịch sử ăn cây trong ván để xử lý tự động
        "an_cay_tracking": {} 
    }
    temp_data = {}

    # --- UI COMPONENT: NÚT BẤM ---
    def create_btn(text, action, bg="blue", color="white", expand=False):
        return ft.Container(
            content=ft.Text(text, size=15, weight="bold", color=color, text_align="center"),
            on_click=action,
            bgcolor=bg,
            padding=12,
            border_radius=8,
            alignment=ft.Alignment(0, 0),
            ink=True,
            expand=expand 
        )

    # --- UI COMPONENT: THẺ NGƯỜI CHƠI ---
    def create_player_card(p):
        money = int(p['money'])
        money_color = "#2E7D32" if money >= 0 else "#C62828"
        bg_money = "#E8F5E9" if money >= 0 else "#FFEBEE"
        
        return ft.Container(
            height=90, 
            bgcolor="white",
            padding=15,
            border_radius=12,
            border=ft.border.all(1, "#D0D0D0"),
            content=ft.Row([
                ft.Row([
                    ft.Container(
                        content=ft.Icon("person", size=24, color="white"),
                        padding=10, bgcolor="#90A4AE", border_radius=50
                    ),
                    ft.Column([
                        ft.Text(p["name"], weight="bold", size=16, color="#37474F"),
                        ft.Container(
                            content=ft.Text("✎ Sửa tên", size=12, color="#1976D2"),
                            on_click=lambda e, x=p: goto_rename(x),
                            padding=ft.padding.only(top=2, bottom=2)
                        )
                    ], spacing=2, alignment="center"),
                ]),
                ft.Container(
                    content=ft.Text(f"{money:,} k", color=money_color, weight="bold", size=16),
                    bgcolor=bg_money, padding=ft.padding.symmetric(horizontal=10, vertical=5), 
                    border_radius=8
                )
            ], alignment="spaceBetween")
        )

    # --- LOGIC GHI LỊCH SỬ TỔNG ---
    def commit_log(title, result_details):
        timestamp = datetime.now().strftime("%H:%M")
        final_details = []
        if state["current_logs"]:
            final_details.append("--- Diễn biến ---")
            final_details.extend(state["current_logs"])
            final_details.append("--- Kết quả ---")
        final_details.extend(result_details)
        state["history"].insert(0, {"time": timestamp, "title": title, "details": final_details})
        state["current_logs"] = [] 
        # Reset tracking ăn cây khi kết thúc ván
        state["an_cay_tracking"] = {}

    # ====================================================================================
    # TÍNH NĂNG MỚI: ĂN CÂY
    # ====================================================================================
    def on_an_cay_loser(loser):
        if not loser: return 
        
        # 1. Kiểm tra xem người này đã bị ăn trước đó chưa
        track = state["an_cay_tracking"].get(loser["name"])
        
        if track: # Nếu đã bị ăn từ cây 1
            count = track["count"]
            if count >= 3:
                page.snack_bar = ft.SnackBar(ft.Text(f"{loser['name']} đã bị ăn tối đa 3 cây!"), bgcolor="red")
                page.snack_bar.open = True; page.update(); return view_dashboard()
            
            # Tự động lấy người được ăn từ lần đầu tiên
            winner_name = track["winner"]
            winner = next(p for p in state["players"] if p["name"] == winner_name)
            process_an_cay(loser, winner, count + 1)
        
        else: # Nếu đây là lần đầu tiên bị ăn
            # Lọc ra những người ĐÃ ĐƯỢC CHỌN làm người được ăn của người khác để loại trừ
            used_winners = [data["winner"] for data in state["an_cay_tracking"].values()]
            
            # Danh sách người có thể nhận cây = Trừ bản thân + Trừ những người đã có 'mối'
            avail_winners = [p for p in state["players"] if p["name"] != loser["name"] and p["name"] not in used_winners]
            
            if not avail_winners:
                page.snack_bar = ft.SnackBar(ft.Text("Không còn người chơi hợp lệ để nhận cây!"), bgcolor="red")
                page.snack_bar.open = True; page.update(); return view_dashboard()
                
            goto_selector(f"Ai ăn cây của {loser['name']}?", avail_winners, lambda w: process_an_cay(loser, w, 1) if w else view_dashboard())

    def process_an_cay(loser, winner, lan_thu):
        if not winner: return view_dashboard()
        
        # Cập nhật cache tracking
        state["an_cay_tracking"][loser["name"]] = {"winner": winner["name"], "count": lan_thu}
        
        # Tính tiền
        he_so = 1 if lan_thu == 1 else (2 if lan_thu == 2 else 4)
        amt = state["bet"] * he_so
        
        loser["money"] -= amt
        winner["money"] += amt
        
        # Ghi log (Có icon phân biệt để Nộp Gà không đếm nhầm)
        state["current_logs"].append(f"♦️ {loser['name']} bị {winner['name']} ăn cây {lan_thu}: -{int(amt)}k / {winner['name']}: +{int(amt)}k")
        
        page.snack_bar = ft.SnackBar(ft.Text(f"{winner['name']} ăn cây {lan_thu} của {loser['name']} (+{int(amt)}k)"), bgcolor="green")
        page.snack_bar.open = True
        view_dashboard()

    # ====================================================================================
    # TÍNH NĂNG MỚI: ĂN CHỐT
    # ====================================================================================
    def on_an_chot_loser(loser):
        if not loser: return
        avail_winners = [p for p in state["players"] if p["name"] != loser["name"]]
        goto_selector(f"Ai ăn CHỐT của {loser['name']}?", avail_winners, lambda w: process_an_chot(loser, w) if w else view_dashboard())

    def process_an_chot(loser, winner):
        if not winner: return view_dashboard()
        
        amt = state["bet"] * 4
        loser["money"] -= amt
        winner["money"] += amt
        
        # Ghi log riêng cho chốt
        state["current_logs"].append(f"🔥 {loser['name']} bị {winner['name']} ăn CHỐT: -{int(amt)}k / {winner['name']}: +{int(amt)}k")
        
        page.snack_bar = ft.SnackBar(ft.Text(f"{winner['name']} ăn CHỐT của {loser['name']} (+{int(amt)}k)"), bgcolor="green")
        page.snack_bar.open = True
        view_dashboard()


    # ====================================================================================
    # PHẦN GIAO DIỆN (VIEWS)
    # ====================================================================================

    # --- MÀN HÌNH CHÍNH (DASHBOARD) ---
    def view_dashboard():
        controls = []
        
        # 1. Header
        info_card = ft.Container(
            height=100, 
            content=ft.Row([
                ft.Column([
                    ft.Text("MỨC CƯỢC", size=12, color="grey", weight="bold"),
                    ft.Text(f"{int(state['bet']):,} K", size=22, weight="bold", color="#333333")
                ], alignment="center", horizontal_alignment="center"),
                ft.Container(width=1, height=40, bgcolor="#DDDDDD"),
                ft.Column([
                    ft.Text("QUỸ GÀ", size=12, color="#F57C00", weight="bold"),
                    ft.Text(f"{int(state['pot']):,} K", size=28, weight="bold", color="#F57C00")
                ], alignment="center", horizontal_alignment="center"),
            ], alignment="spaceEvenly"),
            padding=20, border_radius=15, bgcolor="white",
            border=ft.border.all(1, "#D0D0D0")
        )
        controls.append(info_card)
        controls.append(ft.Container(height=15))

        # 2. Danh sách người chơi
        for p in state["players"]:
            controls.append(create_player_card(p))
            controls.append(ft.Container(height=10))

        controls.append(ft.Container(height=5))

        # 3. Nút chức năng (Đã cập nhật thêm Ăn Cây & Ăn Chốt)
        actions = ft.Column([
            # HÀNG 1: Tính năng mới
            ft.Row([
                ft.Expanded(create_btn("ĂN CÂY", lambda e: goto_selector("Ai bị ăn cây?", state["players"], on_an_cay_loser), bg="#4CAF50")),
                ft.Container(width=10),
                ft.Expanded(create_btn("ĂN CHỐT", lambda e: goto_selector("Ai bị ăn chốt?", state["players"], on_an_chot_loser), bg="#E91E63")),
            ]),
            ft.Container(height=10),
            
            # HÀNG 2: Giữ nguyên nộp gà vô Quỹ & Ù
            ft.Row([
                ft.Expanded(create_btn("NỘP GÀ (QUỸ)", lambda e: goto_selector("Ai nộp gà?", state["players"], on_nop_ga_auto), bg="#FFA726")),
                ft.Container(width=10),
                ft.Expanded(create_btn("XỬ LÝ Ù", lambda e: goto_selector("Ai Ù?", state["players"], on_u_selected), bg="#EF5350")),
            ]),
            ft.Container(height=10),
            
            # HÀNG 3: Xếp hạng
            ft.Row([
                ft.Expanded(create_btn("XẾP HẠNG VÁN ĐẤU", lambda e: goto_selector("Ai NHẤT?", state["players"], on_nhat_selected), bg="#42A5F5"))
            ]),
            ft.Container(height=10),
            
            # HÀNG 4: Công cụ
            ft.Row([
                ft.Expanded(create_btn("LỊCH SỬ", view_history, bg="#78909C")),
                ft.Container(width=10),
                ft.Expanded(create_btn("CÀI ĐẶT", goto_settings, bg="#78909C")),
                ft.Container(width=10),
                ft.Expanded(create_btn("RESET", reset_game, bg="#78909C")),
            ]),
            
            # --- NÚT THOÁT ---
            ft.Container(height=20),
            ft.Row([
                 ft.Expanded(create_btn("THOÁT PHẦN MỀM", lambda e: page.window_close(), bg="#B0BEC5"))
            ]),
            ft.Container(height=50) 
        ])
        controls.append(actions)

        # View chính
        view = ft.View(
            route="/",
            controls=[
                ft.Column(
                    controls=controls, 
                    scroll=ft.ScrollMode.AUTO, 
                    expand=True
                )
            ],
            bgcolor=COLOR_BG,
            padding=ft.padding.only(top=60, left=15, right=15, bottom=20)
        )
        
        page.views.clear()
        page.views.append(view)
        page.update()

    # --- MÀN HÌNH CHỌN (SELECTOR) ---
    def goto_selector(title, items, callback, multi=False):
        controls = []
        controls.append(ft.Container(
            content=ft.Text(title, size=20, weight="bold", color="#333333", text_align="center"),
            padding=ft.padding.only(bottom=20), alignment=ft.alignment.center
        ))

        if not multi:
            for p in items:
                btn = create_btn(p["name"], lambda e, x=p: callback(x), bg="white", color="#1976D2")
                btn.border = ft.border.all(1, "#1976D2")
                controls.append(ft.Row([ft.Expanded(btn)]))
                controls.append(ft.Container(height=8))
        else:
            checks = []
            for p in items:
                cb = ft.Checkbox(label=p["name"], fill_color="#1976D2")
                container = ft.Container(
                    content=cb, padding=10, bgcolor="white", border_radius=8,
                    border=ft.border.all(1, "#E0E0E0")
                )
                checks.append({"cb": cb, "val": p})
                controls.append(container)
                controls.append(ft.Container(height=8))
            
            def submit_multi(e):
                callback([x["val"] for x in checks if x["cb"].value])
            
            controls.append(ft.Container(height=15))
            controls.append(create_btn("XÁC NHẬN", submit_multi, bg="#4CAF50"))

        controls.append(ft.Container(height=20))
        
        # Nút Quay lại
        controls.append(
            ft.Container(
                content=ft.Text("Quay lại", color="grey", text_align="center"),
                on_click=lambda e: page.views.pop() or page.go("/"), 
                padding=15, alignment=ft.alignment.center
            )
        )
        
        view = ft.View(
            route="/selector",
            controls=[ft.Column(controls, scroll=ft.ScrollMode.AUTO, expand=True)],
            bgcolor=COLOR_BG,
            padding=ft.padding.only(top=60, left=15, right=15, bottom=20)
        )
        page.views.append(view)
        page.update()

    # --- CÁC HÀM LOGIC CŨ GIỮ NGUYÊN (Nộp Quỹ Gà) ---
    def on_nop_ga_auto(p):
        if not p: return 
        count = 0
        for log in state["current_logs"]:
            # Chỉ đếm những log cũ (Nộp gà) chứ không đếm log Ăn Cây mới (bắt đầu bằng icon)
            if log.startswith(f"{p['name']}"): count += 1
        
        if count >= 3:
            page.snack_bar = ft.SnackBar(ft.Text(f"{p['name']} đã nộp gà tối đa 3 lần!"), bgcolor="red")
            page.snack_bar.open = True; page.update(); return 
        
        lan_thu = count + 1
        he_so = 1 if lan_thu == 1 else (2 if lan_thu == 2 else 4)
        amt = state["bet"] * he_so
        p["money"] -= amt; state["pot"] += amt
        
        state["current_logs"].append(f"{p['name']} nộp quỹ gà lần {lan_thu}: -{int(amt)}k (Gà +{int(amt)}k)")
        page.snack_bar = ft.SnackBar(ft.Text(f"{p['name']} nộp quỹ gà ({int(amt)}k)"), bgcolor="green")
        page.snack_bar.open = True
        view_dashboard() 

    # --- CÁC HÀM XẾP HẠNG (GIỮ NGUYÊN) ---
    def on_nhat_selected(nhat):
        if not nhat: return 
        temp_data.clear(); temp_data["nhat"] = nhat
        others = [p for p in state["players"] if p != nhat]
        goto_selector("Ai bị MÓM?", others, on_mom_selected, multi=True)

    def on_mom_selected(moms):
        temp_data["moms"] = moms
        nhat = temp_data["nhat"]
        normals = [p for p in state["players"] if p != nhat and p not in moms]
        if len(normals) <= 1:
            if len(normals) == 1: temp_data["nhi"] = normals[0]
            finalize_rank()
        else: goto_selector("Ai về NHÌ?", normals, on_nhi_selected)

    def on_nhi_selected(nhi):
        if not nhi: return finalize_rank()
        temp_data["nhi"] = nhi
        nhat = temp_data["nhat"]; moms = temp_data["moms"]
        remaining = [p for p in state["players"] if p not in [nhat, nhi] + moms]
        if len(remaining) > 1: goto_selector("Ai về BA?", remaining, on_ba_selected)
        else: finalize_rank()

    def on_ba_selected(ba):
        if ba: temp_data["ba"] = ba
        finalize_rank()

    def finalize_rank():
        nhat = temp_data["nhat"]; moms = temp_data["moms"]
        normal_losers = []
        if "nhi" in temp_data: normal_losers.append(temp_data["nhi"])
        if "ba" in temp_data: normal_losers.append(temp_data["ba"])
        accounted = [nhat] + moms + normal_losers
        normal_losers.extend([p for p in state["players"] if p not in accounted])

        total_win = 0; rank_details = []
        for p in moms:
            amt = state["bet"] * 4; p["money"] -= amt; total_win += amt
            rank_details.append(f"{p['name']} (Móm): -{int(amt)}k")
        for i, p in enumerate(normal_losers):
            amt = state["bet"] * (i + 1); p["money"] -= amt; total_win += amt
            rank_name = ["Nhì", "Ba", "Bét"][i] if i < 3 else "Bét"
            rank_details.append(f"{p['name']} ({rank_name}): -{int(amt)}k")
            
        nhat["money"] += total_win
        rank_details.insert(0, f"{nhat['name']} (Nhất): +{int(total_win)}k")
        commit_log("Tổng kết ván", rank_details); temp_data.clear()
        view_dashboard()

    # --- CÁC HÀM XỬ LÝ Ù (GIỮ NGUYÊN) ---
    def on_u_selected(u):
        if not u: return
        temp_data["u"] = u
        goto_selector("Có ai ĐỀN LÀNG không?", [p for p in state["players"] if p != u], on_den_selected)

    def on_den_selected(den):
        u = temp_data["u"]; tien = state["bet"] * 5; u_details = []
        if den:
            phat = tien * 3; den["money"] -= phat; u["money"] += phat
            u_details.append(f"{den['name']} đền: -{int(phat)}k")
        else:
            for p in state["players"]:
                if p != u: p["money"] -= tien; u["money"] += tien; u_details.append(f"{p['name']}: -{int(tien)}k")
        if state["pot"] > 0:
            u["money"] += state["pot"]; u_details.append(f"Ăn gà: +{int(state['pot'])}k"); state["pot"] = 0
        u_details.insert(0, f"{u['name']} Ù"); commit_log("Ván Ù", u_details)
        view_dashboard()

    # --- MÀN HÌNH LỊCH SỬ ---
    def view_history(e):
        controls = [ft.Text("Lịch sử đấu", size=24, weight="bold", color="#333333")]
        if not state["history"]: controls.append(ft.Text("Trống", color="grey"))
        else:
            for log in state["history"]:
                detail_col = ft.Column(spacing=2)
                for line in log["details"]:
                    txt_color = "green" if "+" in line else ("red" if "-" in line else "black")
                    if "---" in line: txt_color = "grey"
                    detail_col.controls.append(ft.Text(line, size=14, color=txt_color))
                controls.append(ft.Container(
                    content=ft.Column([
                        ft.Row([ft.Text(log["title"], weight="bold"), ft.Text(log["time"], size=12, color="grey")], alignment="spaceBetween"),
                        ft.Divider(height=1), detail_col
                    ]), padding=15, bgcolor="white", border_radius=10, border=ft.border.all(1, "#EEEEEE")
                ))
        controls.append(ft.Container(height=20))
        controls.append(create_btn("QUAY LẠI", lambda e: page.views.pop() or page.go("/"), bg="grey"))
        
        view = ft.View(
            route="/history", 
            controls=[ft.Column(controls, scroll=ft.ScrollMode.AUTO, expand=True)], 
            bgcolor=COLOR_BG, padding=ft.padding.only(top=60, left=15, right=15, bottom=20)
        )
        page.views.append(view); page.update()

    # --- ĐỔI TÊN & SETTINGS ---
    def goto_rename(player):
        tf_name = ft.TextField(label="Tên mới", value=player["name"], text_align="center", text_size=20)
        def save(e): 
            if tf_name.value.strip(): player["name"] = tf_name.value.strip()
            view_dashboard()
        
        controls = [ft.Text("Đổi tên", size=24), tf_name, create_btn("LƯU", save, bg="#4CAF50"), create_btn("HỦY", lambda e: page.views.pop() or page.go("/"), bg="grey")]
        view = ft.View(route="/rename", controls=controls, bgcolor=COLOR_BG, padding=ft.padding.only(top=60, left=15, right=15, bottom=20))
        page.views.append(view); page.update()

    def goto_settings(e):
        tf = ft.TextField(value=str(int(state["bet"])), text_align="center", keyboard_type="number")
        def save(e):
            try: state["bet"] = float(tf.value)
            except: pass
            view_dashboard()
        
        controls = [ft.Text("Cài đặt cược", size=24), tf, create_btn("LƯU", save, bg="#4CAF50"), create_btn("HỦY", lambda e: page.views.pop() or page.go("/"), bg="grey")]
        view = ft.View(route="/settings", controls=controls, bgcolor=COLOR_BG, padding=ft.padding.only(top=60, left=15, right=15, bottom=20))
        page.views.append(view); page.update()

    def reset_game(e):
        for p in state["players"]: p["money"] = 0
        state["pot"] = 0; state["history"] = []; state["current_logs"] = []
        state["an_cay_tracking"] = {}
        view_dashboard()

    # Khởi chạy màn hình chính
    view_dashboard()

ft.app(target=main)
