import flet as ft
from datetime import datetime

# --- CẤU HÌNH ---
DEF_BET = 10
PLAYERS_DEF = ["Người 1", "Người 2", "Người 3", "Người 4"]

def main(page: ft.Page):
    # Cấu hình trang chuẩn Mobile
    page.title = "TÁ LẢ PRO"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.scroll = ft.ScrollMode.HIDDEN 
    page.bgcolor = "#F0F2F5" 
    page.padding = 0 
    page.horizontal_alignment = ft.CrossAxisAlignment.STRETCH 

    # --- BIẾN TOÀN CỤC ---
    state = {
        "bet": DEF_BET,
        "pot": 0,
        "players": [{"name": n, "money": 0} for n in PLAYERS_DEF],
        "history": [],      
        "current_logs": []
    }

    # --- HÀM XỬ LÝ GESTURE (VUỐT) ---
    def handle_swipe(e, on_back):
        # Nếu vận tốc vuốt ngang lớn
        if abs(e.primary_velocity) > 500: 
            on_back()

    def wrap_content(controls, on_back_action, pad_top=50):
        """Bao bọc nội dung để bắt sự kiện vuốt"""
        main_col = ft.Column(
            controls=controls, 
            scroll=ft.ScrollMode.AUTO, 
            expand=True,
            spacing=10
        )
        container = ft.Container(
            content=main_col,
            padding=ft.padding.only(top=pad_top, left=15, right=15, bottom=20),
            expand=True,
            bgcolor="#F0F2F5"
        )
        return ft.GestureDetector(
            content=container,
            on_horizontal_drag_end=lambda e: handle_swipe(e, on_back_action),
            expand=True
        )

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

    # --- HÀM GHI LỊCH SỬ ---
    def commit_log(title, result_details):
        timestamp = datetime.now().strftime("%H:%M")
        final_details = []
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
        state["current_logs"] = []

    # --- HÀM THOÁT APP ---
    def exit_app(e=None):
        page.window_close()

    # --- MÀN HÌNH CHÍNH ---
    def view_dashboard(e=None):
        page.clean()

        # 1. Info UI
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

        # 2. Player List UI
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
                ), elevation=0
            )
            list_col.controls.append(card)

        # 3. Actions UI
        actions = ft.Column([
            ft.Container(height=10), 
            ft.Row([
                create_btn("NỘP GÀ", lambda e: nop_ga_flow(), bg="#FFA726"),
                create_btn("XỬ LÝ Ù", lambda e: u_flow_step1_who(), bg="#EF5350"),
            ]),
            ft.Row([
                create_btn("XẾP HẠNG VÁN THƯỜNG", lambda e: rank_flow_step1_nhat(), bg="#42A5F5"),
            ]),
            ft.Row([
                create_btn("XEM LỊCH SỬ", view_history, bg="#607D8B"),
            ]),
            ft.Row([
                create_btn("Cài đặt", goto_settings, bg="#90A4AE"),
                create_btn("Reset", reset_game, bg="#90A4AE"),
            ]),
            ft.Row([
                create_btn("THOÁT", exit_app, bg="#37474F"), 
            ])
        ], spacing=12)

        page.add(wrap_content([info_card, list_col, actions], on_back_action=exit_app))
        page.update()

    # --- MÀN HÌNH CHỌN GENERIC (QUAN TRỌNG) ---
    # on_submit: Hàm chạy khi chọn xong (tiến tới bước sau)
    # on_back: Hàm chạy khi vuốt/ấn back (quay về bước trước)
    def goto_selector(title, items, on_submit, on_back, multi=False):
        page.clean()
        controls = []
        controls.append(ft.Container(
            content=ft.Text(title, size=22, weight="bold", color="#333333", text_align="center"),
            padding=ft.padding.only(top=20, bottom=20),
            alignment=ft.Alignment(0, 0)
        ))

        if not multi:
            for p in items:
                # Khi chọn 1 người, gọi on_submit với người đó
                btn = create_btn(p["name"], lambda e, x=p: on_submit(x), bg="white", color="#1976D2")
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

            def handle_multi_submit(e):
                selected = [x["val"] for x in checks if x["cb"].value]
                on_submit(selected)

            controls.append(ft.Container(height=20))
            controls.append(ft.Row([create_btn("XÁC NHẬN", handle_multi_submit, bg="#4CAF50")]))

        controls.append(ft.Container(height=20))
        # Nút Quay lại gọi trực tiếp hàm on_back
        controls.append(ft.Row([create_btn("Quay lại", lambda e: on_back(), bg="transparent", color="grey")]))

        # Vuốt ngang cũng gọi on_back
        page.add(wrap_content(controls, on_back_action=on_back))
        page.update()

    # ========================================================
    # FLOW 1: NỘP GÀ
    # ========================================================
    def nop_ga_flow():
        # Back về dashboard
        goto_selector("Ai bị ăn (Nộp gà)?", state["players"], 
                      on_submit=process_nop_ga, 
                      on_back=view_dashboard)

    def process_nop_ga(p):
        if not p: return # Should not happen unless logic error

        count = 0
        for log in state["current_logs"]:
            if log.startswith(f"{p['name']}"):
                count += 1

        if count >= 3:
            page.snack_bar = ft.SnackBar(ft.Text(f"LỖI: {p['name']} đã bị ăn đủ 3 cây!"), bgcolor="red")
            page.snack_bar.open = True
            page.update()
            # Ở lại màn hình chọn
            nop_ga_flow() 
            return

        lan_thu = count + 1
        he_so = 1 if lan_thu == 1 else (2 if lan_thu == 2 else 4)
        amt = state["bet"] * he_so

        p["money"] -= amt
        state["pot"] += amt

        log_str = f"{p['name']} bị ăn cây {lan_thu}: -{int(amt)}k (Gà +{int(amt)}k)"
        state["current_logs"].append(log_str)

        page.snack_bar = ft.SnackBar(ft.Text(f"Đã thu {p['name']} cây thứ {lan_thu}"), bgcolor="green")
        page.snack_bar.open = True
        view_dashboard()

    # ========================================================
    # FLOW 2: XẾP HẠNG (RANKING)
    # Step 1 -> Step 2 -> Step 3 -> Step 4 (Final)
    # ========================================================

    # BƯỚC 1: Chọn NHẤT
    def rank_flow_step1_nhat():
        goto_selector("Ai NHẤT?", state["players"], 
                      on_submit=lambda nhat: rank_flow_step2_mom(nhat), 
                      on_back=view_dashboard)

    # BƯỚC 2: Chọn MÓM
    def rank_flow_step2_mom(nhat):
        others = [p for p in state["players"] if p != nhat]
        # Back quay lại bước 1
        goto_selector("Chọn những người MÓM:", others, 
                      on_submit=lambda moms: rank_flow_step3_nhi(nhat, moms), 
                      on_back=rank_flow_step1_nhat, 
                      multi=True)

    # BƯỚC 3: Chọn NHÌ
    def rank_flow_step3_nhi(nhat, moms):
        normals = [p for p in state["players"] if p != nhat and p not in moms]

        # Nếu chỉ còn 1 người hoặc 0 người thì không cần chọn Nhì, tính điểm luôn
        if len(normals) == 0:
            finalize_rank(nhat, moms, None, None)
            return
        elif len(normals) == 1:
            finalize_rank(nhat, moms, normals[0], None)
            return

        # Back quay lại bước 2 (truyền lại nhat để bước 2 render đúng)
        goto_selector("Ai về NHÌ?", normals, 
                      on_submit=lambda nhi: rank_flow_step4_ba(nhat, moms, nhi), 
                      on_back=lambda: rank_flow_step2_mom(nhat))

    # BƯỚC 4: Chọn BA (nếu cần)
    def rank_flow_step4_ba(nhat, moms, nhi):
        remaining = [p for p in state["players"] if p != nhat and p not in moms and p != nhi]

        if len(remaining) > 1:
            # Back quay lại bước 3
            goto_selector("Ai về BA?", remaining, 
                          on_submit=lambda ba: finalize_rank(nhat, moms, nhi, ba), 
                          on_back=lambda: rank_flow_step3_nhi(nhat, moms))
        else:
            finalize_rank(nhat, moms, nhi, None)

    # TÍNH TOÁN CUỐI CÙNG
    def finalize_rank(nhat, moms, nhi, ba):
        normal_losers = []
        if nhi: normal_losers.append(nhi)
        if ba: normal_losers.append(ba)

        accounted = [nhat] + moms + normal_losers
        remaining = [p for p in state["players"] if p not in accounted]
        normal_losers.extend(remaining) # Người còn lại là bét

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
        view_dashboard()

    # ========================================================
    # FLOW 3: XỬ LÝ Ù
    # Step 1 -> Step 2
    # ========================================================

    # BƯỚC 1: Ai Ù
    def u_flow_step1_who():
        goto_selector("Ai Ù?", state["players"], 
                      on_submit=lambda u: u_flow_step2_den(u), 
                      on_back=view_dashboard)

    # BƯỚC 2: Ai Đền (hoặc không ai đền)
    def u_flow_step2_den(u_player):
        others = [p for p in state["players"] if p != u_player]
        # Back quay lại bước 1
        goto_selector("Có ai ĐỀN LÀNG không?", others, 
                      on_submit=lambda den: finalize_u(u_player, den), 
                      on_back=u_flow_step1_who)

    def finalize_u(u, den):
        # Lưu ý: den có thể là None nếu người dùng chọn "Quay lại" ở bước chọn người đền?
        # Không, nút Quay lại ở goto_selector gọi on_back (step1).
        # Nhưng ở màn hình này ta nên có nút "Không ai đền" riêng? 
        # Hiện tại goto_selector bắt buộc chọn 1 người.
        # -> Ta cần một nút "Không ai đền" để xử lý Ù thường. 
        # Tuy nhiên để đơn giản code, nếu người dùng muốn chọn "Không đền", 
        # ở đây ta check logic: Nếu người dùng không chọn ai mà ấn xác nhận (logic checkbox)? 
        # Nhưng đây là single choice button.

        # Để fix: Ta sẽ thêm một lựa chọn "Không ai đền" giả vào danh sách hoặc xử lý riêng.
        # Nhưng đơn giản nhất: Ở màn hình chọn đền, nếu ấn "Quay lại" thì về chọn Ù.
        # Nếu muốn Ù thường -> Cần 1 nút "Không ai đền". 
        # Trong giới hạn UI hiện tại, tôi sẽ xử lý như sau:
        # Nếu hàm gọi có den (là 1 user) -> Đền. 
        # Nhưng nếu muốn Ù thường, người dùng làm sao chọn?
        # -> Tôi sẽ thêm logic: Nếu vào màn hình Đền, ta sẽ thêm 1 item ảo là "KHÔNG AI ĐỀN" vào đầu danh sách others.
        pass # Logic này xử lý bên dưới

    # Viết lại hàm u_flow_step2_den để thêm nút "Không ai đền"
    def u_flow_step2_den(u_player):
        others = [p for p in state["players"] if p != u_player]
        # Tạo object giả
        no_one = {"name": "❌ KHÔNG AI ĐỀN", "id": "nobody"}
        opts = [no_one] + others

        def handle_choice(choice):
            if choice.get("id") == "nobody":
                finalize_u(u_player, None)
            else:
                finalize_u(u_player, choice)

        goto_selector("Ai phải ĐỀN?", opts, 
                      on_submit=handle_choice, 
                      on_back=u_flow_step1_who)

    def finalize_u(u, den):
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

    # --- CÁC MÀN HÌNH KHÁC ---
    def view_history(e=None):
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

        # Back -> Dashboard
        page.add(wrap_content(controls, on_back_action=view_dashboard))
        page.update()

    def goto_rename(player):
        page.clean()
        tf_name = ft.TextField(label="Nhập tên mới", value=player["name"], text_align="center", text_size=20, autofocus=True)
        def save_name(e):
            if tf_name.value.strip(): player["name"] = tf_name.value.strip()
            view_dashboard()

        controls = [
            ft.Container(content=ft.Text("Đổi tên", size=24, weight="bold"), alignment=ft.Alignment(0, 0), padding=20),
            tf_name, ft.Container(height=20), ft.Row([create_btn("LƯU TÊN", save_name, bg="#4CAF50")])
        ]
        # Back -> Dashboard
        page.add(wrap_content(controls, on_back_action=view_dashboard))
        page.update()

    def goto_settings(e):
        page.clean()
        tf = ft.TextField(label="Nhập mức cược mới", value=str(int(state["bet"])), text_align="center", text_size=20)
        def save(e):
            try: state["bet"] = float(tf.value)
            except: pass
            view_dashboard()

        controls = [
            ft.Container(content=ft.Text("Cài đặt", size=24, weight="bold"), alignment=ft.Alignment(0, 0), padding=20),
            tf, ft.Container(height=20), ft.Row([create_btn("LƯU CÀI ĐẶT", save, bg="#4CAF50")])
        ]
        # Back -> Dashboard
        page.add(wrap_content(controls, on_back_action=view_dashboard))
        page.update()

    def reset_game(e):
        for p in state["players"]: p["money"] = 0
        state["pot"] = 0
        state["history"] = []
        state["current_logs"] = []
        view_dashboard()

    view_dashboard()

ft.app(target=main)
