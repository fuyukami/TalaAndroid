import flet as ft
from datetime import datetime

# --- CẤU HÌNH ---
DEF_BET = 10
PLAYERS_DEF = ["Người 1", "Người 2", "Người 3", "Người 4"]

def main(page: ft.Page):
    # Cấu hình trang chuẩn Mobile
    page.title = "TÁ LẢ PRO"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.scroll = ft.ScrollMode.AUTO
    page.bgcolor = "#F0F2F5" 
    page.padding = 10
    page.horizontal_alignment = ft.CrossAxisAlignment.STRETCH 

    # --- BIẾN TOÀN CỤC ---
    state = {
        "bet": DEF_BET,
        "pot": 0,
        "players": [{"name": n, "money": 0} for n in PLAYERS_DEF],
        "history": [],      
        "current_logs": []  # Lịch sử tạm của ván hiện tại
    }

    # Biến tạm
    temp_data = {}

    # --- HÀM TẠO NÚT ---
    def create_btn(text, action, bg="blue", color="white", expand=True):
        return ft.ElevatedButton(
            content=ft.Container(
                content=ft.Text(text, size=16, weight="bold", color=color),
                padding=10,
            ),
            on_click=action,
            bgcolor=bg,
            style=ft.ButtonStyle(
                shape=ft.RoundedRectangleBorder(radius=8),
            ),
            expand=expand 
        )

    # --- HÀM GHI LỊCH SỬ CHÍNH THỨC ---
    def commit_log(title, result_details):
        timestamp = datetime.now().strftime("%H:%M")
        final_details = []

        # Gộp diễn biến ăn cây trước
        if state["current_logs"]:
            final_details.append("--- Diễn biến ---")
            final_details.extend(state["current_logs"])
            final_details.append("--- Kết quả ---")

        final_details.extend(result_details)

        log_entry = {
            "time": timestamp,
            "title": title,
            "details": final_details
        }
        state["history"].insert(0, log_entry)
        state["current_logs"] = [] # Reset log tạm

    # --- MÀN HÌNH CHÍNH ---
    def view_dashboard():
        page.clean()

        # 1. Thanh thông tin
        txt_bet = ft.Text(f"{int(state['bet']):,} k", size=20, weight="bold", color="#333333")
        txt_pot = ft.Text(f"{int(state['pot']):,} k", size=28, weight="bold", color="#FFC107")

        info_card = ft.Container(
            content=ft.Row([
                ft.Column([ft.Text("Mức cược", size=13, color="grey"), txt_bet], alignment="center"),
                ft.VerticalDivider(width=1, color="#DDDDDD"),
                ft.Column([ft.Text("QUỸ GÀ", size=13, weight="bold", color="grey"), txt_pot], alignment="center"),
            ], alignment="spaceEvenly"),
            padding=15, border_radius=12, bgcolor="white", height=90, 
            shadow=ft.BoxShadow(blur_radius=10, color="#1A000000") 
        )

        # 2. Danh sách người chơi
        list_col = ft.Column(spacing=10)
        for p in state["players"]:
            money_color = "#4CAF50" if p["money"] >= 0 else "#E53935"
            bg_money = "#E8F5E9" if p["money"] >= 0 else "#FFEBEE"

            card = ft.Card(
                content=ft.Container(
                    content=ft.Row([
                        ft.Row([
                            ft.Text("👤", size=28),
                            ft.Column([
                                ft.Text(p["name"], weight="bold", size=16, color="#444444"),
                                ft.Container(
                                    content=ft.Text("✎ Sửa tên", size=12, color="blue"),
                                    on_click=lambda e, x=p: goto_rename(x),
                                    padding=ft.padding.only(top=2, bottom=2)
                                )
                            ], spacing=2),
                        ]),
                        ft.Container(
                            content=ft.Text(f"{int(p['money']):,} k", color=money_color, weight="bold", size=15),
                            bgcolor=bg_money, padding=8, border_radius=6
                        )
                    ], alignment="spaceBetween"),
                    padding=15, bgcolor="white", border_radius=10
                ),
                elevation=0
            )
            list_col.controls.append(card)

        # 3. Nút chức năng
        actions = ft.Column([
            ft.Container(height=10), 
            ft.Row([
                create_btn("NỘP GÀ (ĂN CÂY)", lambda e: goto_selector("Ai bị ăn (Nộp gà)?", state["players"], on_nop_ga_auto), bg="#FFA726"),
                create_btn("XỬ LÝ Ù", lambda e: goto_selector("Ai Ù?", state["players"], on_u_selected), bg="#EF5350"),
            ]),
            ft.Row([
                create_btn("XẾP HẠNG VÁN THƯỜNG", lambda e: goto_selector("Ai NHẤT?", state["players"], on_nhat_selected), bg="#42A5F5"),
            ]),
            ft.Row([
                create_btn("XEM LỊCH SỬ", view_history, bg="#607D8B"),
            ]),
            ft.Row([
                create_btn("Cài đặt", goto_settings, bg="#90A4AE"),
                create_btn("Reset", reset_game, bg="#90A4AE"),
            ])
        ], spacing=12)

        page.add(info_card, list_col, actions)
        page.update()

    # --- MÀN HÌNH CHỌN (CHUNG) ---
    def goto_selector(title, items, callback, multi=False):
        page.clean()
        controls = []
        controls.append(ft.Container(
            content=ft.Text(title, size=22, weight="bold", color="#333333", text_align="center"),
            padding=ft.padding.only(top=20, bottom=20),
            alignment=ft.Alignment(0, 0)
        ))
        if not multi:
            for p in items:
                btn = create_btn(p["name"], lambda e, x=p: callback(x), bg="white", color="#1976D2")
                btn.style.side = ft.BorderSide(1, "#1976D2")
                controls.append(ft.Row([btn]))
        else:
            checks = []
            for p in items:
                cb = ft.Checkbox(label=p["name"], fill_color="#1976D2")
                container = ft.Container(
                    content=cb, padding=15, bgcolor="white", border_radius=8,
                    border=ft.border.all(1, "#EEEEEE")
                )
                checks.append({"cb": cb, "val": p})
                controls.append(container)
            def submit_multi(e):
                callback([x["val"] for x in checks if x["cb"].value])
            controls.append(ft.Container(height=20))
            controls.append(ft.Row([create_btn("XÁC NHẬN", submit_multi, bg="#4CAF50")]))

        controls.append(ft.Container(height=20))
        controls.append(ft.Row([create_btn("Quay lại / Bỏ qua", lambda e: (callback(None) if not multi else callback([])), bg="transparent", color="grey")]))
        page.add(ft.Column(controls))
        page.update()

    # ========================================================
    # LOGIC NỘP GÀ MỚI (TỰ ĐỘNG ĐẾM & TÍNH TIỀN)
    # ========================================================
    def on_nop_ga_auto(p):
        if not p: return view_dashboard()

        # 1. Quét lịch sử tạm để đếm số lần người này đã bị ăn
        count = 0
        for log in state["current_logs"]:
            # Kiểm tra tên người chơi có ở đầu dòng log không
            if log.startswith(f"{p['name']}"):
                count += 1

        # 2. Kiểm tra giới hạn (Tối đa 3 cây)
        if count >= 3:
            page.snack_bar = ft.SnackBar(ft.Text(f"LỖI: {p['name']} đã bị ăn đủ 3 cây! Không thể nộp thêm."), bgcolor="red")
            page.snack_bar.open = True
            page.update()
            return view_dashboard()

        # 3. Tính tiền dựa trên lần thứ mấy (count = 0 là lần 1)
        lan_thu = count + 1
        he_so = 0

        if lan_thu == 1: he_so = 1   # Cây 1: 1 cược
        elif lan_thu == 2: he_so = 2 # Cây 2: 2 cược
        elif lan_thu == 3: he_so = 4 # Cây 3 (Chốt): 4 cược

        amt = state["bet"] * he_so

        # 4. Trừ tiền và lưu log
        p["money"] -= amt
        state["pot"] += amt

        # Log ghi rõ lần thứ mấy để dễ kiểm tra
        log_str = f"{p['name']} bị ăn cây {lan_thu}: -{int(amt)}k (Gà +{int(amt)}k)"
        state["current_logs"].append(log_str)

        # Thông báo thành công
        page.snack_bar = ft.SnackBar(ft.Text(f"Đã thu {p['name']} cây thứ {lan_thu} ({int(amt)}k)"), bgcolor="green")
        page.snack_bar.open = True

        view_dashboard()

    # --- LOGIC XẾP HẠNG ---
    def on_nhat_selected(nhat):
        if not nhat: return view_dashboard()
        temp_data.clear()
        temp_data["nhat"] = nhat
        others = [p for p in state["players"] if p != nhat]
        goto_selector("Chọn những người MÓM:", others, on_mom_selected, multi=True)

    def on_mom_selected(moms):
        temp_data["moms"] = moms
        nhat = temp_data["nhat"]
        normals = [p for p in state["players"] if p != nhat and p not in moms]

        if len(normals) == 0: finalize_rank()
        elif len(normals) == 1:
            temp_data["nhi"] = normals[0]
            finalize_rank()
        else:
            goto_selector("Ai về NHÌ?", normals, on_nhi_selected)

    def on_nhi_selected(nhi):
        if not nhi: return finalize_rank()
        temp_data["nhi"] = nhi
        nhat = temp_data["nhat"]
        moms = temp_data["moms"]
        remaining = [p for p in state["players"] if p != nhat and p not in moms and p != nhi]

        if len(remaining) > 1:
            goto_selector("Ai về BA?", remaining, on_ba_selected)
        else:
            finalize_rank()

    def on_ba_selected(ba):
        if ba: temp_data["ba"] = ba
        finalize_rank()

    def finalize_rank():
        nhat = temp_data["nhat"]
        moms = temp_data["moms"]

        normal_losers = []
        if "nhi" in temp_data: normal_losers.append(temp_data["nhi"])
        if "ba" in temp_data: normal_losers.append(temp_data["ba"])

        accounted = [nhat] + moms + normal_losers
        remaining = [p for p in state["players"] if p not in accounted]
        normal_losers.extend(remaining)

        total_win = 0
        rank_details = []

        for p in moms:
            amt = state["bet"] * 4
            p["money"] -= amt
            total_win += amt
            rank_details.append(f"{p['name']} (Móm): -{int(amt)}k")

        for i, p in enumerate(normal_losers):
            k = i + 1 
            amt = state["bet"] * k
            p["money"] -= amt
            total_win += amt
            rank_name = "Nhì" if i==0 else ("Ba" if i==1 else "Bét")
            rank_details.append(f"{p['name']} ({rank_name}): -{int(amt)}k")

        nhat["money"] += total_win
        rank_details.insert(0, f"{nhat['name']} (Nhất): +{int(total_win)}k")

        commit_log("Tổng kết ván", rank_details)
        temp_data.clear()
        view_dashboard()

    # --- LOGIC Ù ---
    def on_u_selected(u):
        if not u: return view_dashboard()
        temp_data["u"] = u
        others = [p for p in state["players"] if p != u]
        goto_selector("Có ai ĐỀN LÀNG không?", others, on_den_selected)

    def on_den_selected(den):
        u = temp_data["u"]
        tien = state["bet"] * 5
        u_details = []

        if den:
            phat = tien * 3
            den["money"] -= phat
            u["money"] += phat
            u_details.append(f"{den['name']} đền: -{int(phat)}k")
            u_details.append(f"{u['name']} ù: +{int(phat)}k")
        else:
            for p in state["players"]:
                if p != u: 
                    p["money"] -= tien
                    u["money"] += tien
                    u_details.append(f"{p['name']}: -{int(tien)}k")
            u_details.insert(0, f"{u['name']} ù: +{int(tien * 3)}k")

        if state["pot"] > 0:
            u["money"] += state["pot"]
            u_details.append(f"{u['name']} ăn gà: +{int(state['pot'])}k")
            state["pot"] = 0

        commit_log("Ván Ù", u_details)
        view_dashboard()

    # --- MÀN HÌNH LỊCH SỬ ---
    def view_history(e):
        page.clean()
        controls = []
        controls.append(ft.Container(
            content=ft.Text("Lịch sử đấu", size=24, weight="bold", color="#333333"),
            alignment=ft.Alignment(0, 0), padding=20
        ))
        if not state["history"]:
            controls.append(ft.Container(content=ft.Text("Chưa có ván đấu nào", color="grey"), alignment=ft.Alignment(0, 0)))
        else:
            for log in state["history"]:
                detail_col = ft.Column(spacing=2)
                for line in log["details"]:
                    if "---" in line:
                        detail_col.controls.append(ft.Text(line, size=12, color="grey", italic=True, weight="bold"))
                    else:
                        txt_color = "green" if "+" in line else ("red" if "-" in line else "black")
                        detail_col.controls.append(ft.Text(line, size=14, color=txt_color))
                card = ft.Card(
                    content=ft.Container(
                        content=ft.Column([
                            ft.Row([ft.Text(log["title"], weight="bold", size=16), ft.Text(log["time"], size=12, color="grey")], alignment="spaceBetween"),
                            ft.Divider(height=1, color="#EEEEEE"),
                            detail_col
                        ]), padding=15, bgcolor="white", border_radius=10
                    ), elevation=0
                )
                controls.append(card)
        controls.append(ft.Container(height=20))
        controls.append(ft.Row([create_btn("QUAY LẠI", lambda e: view_dashboard(), bg="grey")]))
        page.add(ft.Column(controls))
        page.update()

    # --- ĐỔI TÊN & SETTINGS ---
    def goto_rename(player):
        page.clean()
        tf_name = ft.TextField(label="Nhập tên mới", value=player["name"], text_align="center", text_size=20, autofocus=True)
        def save_name(e):
            if tf_name.value.strip(): player["name"] = tf_name.value.strip()
            view_dashboard()
        page.add(
            ft.Container(content=ft.Text("Đổi tên", size=24, weight="bold"), alignment=ft.Alignment(0, 0), padding=20),
            tf_name, ft.Container(height=20), ft.Row([create_btn("LƯU TÊN", save_name, bg="#4CAF50")])
        )
        page.update()

    def goto_settings(e):
        page.clean()
        tf = ft.TextField(label="Nhập mức cược mới", value=str(int(state["bet"])), text_align="center", text_size=20)
        def save(e):
            try: state["bet"] = float(tf.value)
            except: pass
            view_dashboard()
        page.add(
            ft.Container(content=ft.Text("Cài đặt", size=24, weight="bold"), alignment=ft.Alignment(0, 0), padding=20),
            tf, ft.Container(height=20), ft.Row([create_btn("LƯU CÀI ĐẶT", save, bg="#4CAF50")])
        )
        page.update()

    def reset_game(e):
        for p in state["players"]: p["money"] = 0
        state["pot"] = 0
        state["history"] = []
        state["current_logs"] = []
        view_dashboard()

    view_dashboard()

ft.app(target=main)
