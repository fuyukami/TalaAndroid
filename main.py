import flet as ft
from datetime import datetime
import logging

# --- CẤU HÌNH ---
logging.basicConfig(level=logging.INFO)

# Bảng màu An Toàn (Solid Colors)
COLOR_BG = "#F0F2F5"          
COLOR_CARD = "#FFFFFF"        
COLOR_TEXT = "#333333"   
COLOR_GOLD = "#F1C40F"        
COLOR_BTN_BLUE = "#3498DB"
COLOR_BTN_BLUE_SHADE = "#2980B9" # Màu tối hơn để làm chân nút
COLOR_BTN_RED = "#E74C3C"
COLOR_BTN_RED_SHADE = "#C0392B"
COLOR_BTN_ORANGE = "#E67E22"
COLOR_BTN_ORANGE_SHADE = "#D35400"
COLOR_BTN_GREY = "#95A5A6"
COLOR_BTN_GREY_SHADE = "#7F8C8D"

DEF_BET = 10
PLAYERS_DEF = ["Người 1", "Người 2", "Người 3", "Người 4"]

def main(page: ft.Page):
    try:
        page.title = "TÁ LẢ PRO"
        page.theme_mode = ft.ThemeMode.LIGHT
        page.bgcolor = COLOR_BG
        page.padding = 0 
        page.safe_area = True 

        # --- BIẾN TOÀN CỤC ---
        state = {
            "bet": DEF_BET,
            "pot": 0,
            "players": [{"name": n, "money": 0} for n in PLAYERS_DEF],
            "history": [],      
            "current_logs": []
        }
        temp_data = {}

        # --- UI: NÚT GIẢ 3D (Dùng Border, KHÔNG dùng Shadow) ---
        def create_safe_btn(text, action, main_color, shade_color):
            return ft.Container(
                content=ft.Text(text, size=14, weight="bold", color="white", text_align="center"),
                on_click=action,
                alignment=ft.Alignment(0, 0),
                height=50,
                border_radius=8,
                bgcolor=main_color,
                # Tạo hiệu ứng 3D bằng viền dưới dày hơn
                border=ft.border.only(
                    bottom=ft.BorderSide(4, shade_color),
                    top=ft.BorderSide(0, "transparent"),
                    left=ft.BorderSide(0, "transparent"),
                    right=ft.BorderSide(0, "transparent"),
                ),
                ink=True, expand=True
            )

        # --- UI: THẺ NGƯỜI CHƠI ---
        def create_player_card(p):
            money = int(p['money'])
            txt_color = "#27AE60" if money >= 0 else "#C0392B"
            
            return ft.Container(
                padding=10, border_radius=10, bgcolor="white",
                border=ft.border.all(1, "#BDC3C7"), # Viền xám nhẹ
                content=ft.Row([
                    ft.Row([
                        ft.Container(
                            content=ft.Icon("person", size=20, color="white"),
                            padding=8, bgcolor=COLOR_GOLD, border_radius=50,
                        ),
                        ft.Column([
                            ft.Text(p["name"], weight="bold", size=15, color=COLOR_TEXT),
                            ft.Container(
                                content=ft.Text("✎ Sửa tên", size=11, color="grey"),
                                on_click=lambda e, x=p: goto_rename(x),
                                padding=ft.padding.only(top=2, bottom=2)
                            )
                        ], spacing=2),
                    ]),
                    ft.Text(f"{money:,} k", color=txt_color, weight="bold", size=16),
                ], alignment="spaceBetween")
            )

        # --- LOGIC GHI LOG ---
        def commit_log(title, result_details):
            timestamp = datetime.now().strftime("%H:%M")
            final = []
            if state["current_logs"]:
                final.append("--- Diễn biến ---")
                final.extend(state["current_logs"])
                final.append("--- Kết quả ---")
            final.extend(result_details)
            state["history"].insert(0, {"time": timestamp, "title": title, "details": final})
            state["current_logs"] = []

        # --- MÀN HÌNH CHÍNH (DÙNG LISTVIEW ĐỂ TRÁNH TRÀN MÀN HÌNH) ---
        def view_dashboard():
            page.clean()

            # 1. Header
            header = ft.Container(
                padding=20, bgcolor="#2C3E50",
                content=ft.Row([
                    ft.Column([
                        ft.Text("MỨC CƯỢC", size=12, color="#BDC3C7"),
                        ft.Text(f"{int(state['bet']):,} K", size=24, weight="bold", color="white")
                    ], horizontal_alignment="center", expand=True),
                    ft.Container(width=1, height=40, bgcolor="#7F8C8D"),
                    ft.Column([
                        ft.Text("QUỸ GÀ", size=12, color=COLOR_GOLD),
                        ft.Text(f"{int(state['pot']):,} K", size=30, weight="bold", color=COLOR_GOLD)
                    ], horizontal_alignment="center", expand=True),
                ])
            )

            # 2. Player List Items
            items = [header, ft.Container(height=10)]
            for p in state["players"]:
                items.append(create_player_card(p))
                items.append(ft.Container(height=8))

            # 3. Actions Items
            items.append(ft.Container(height=10))
            items.append(ft.Row([
                create_safe_btn("NỘP GÀ", lambda e: goto_selector("AI BỊ ĂN?", state["players"], on_nop_ga_auto), COLOR_BTN_ORANGE, COLOR_BTN_ORANGE_SHADE),
                create_safe_btn("XỬ LÝ Ù", lambda e: goto_selector("AI Ù?", state["players"], on_u_selected), COLOR_BTN_RED, COLOR_BTN_RED_SHADE),
            ], spacing=10))
            
            items.append(ft.Container(height=10))
            items.append(create_safe_btn("XẾP HẠNG VÁN ĐẤU", lambda e: goto_selector("AI VỀ NHẤT?", state["players"], on_nhat_selected), COLOR_BTN_BLUE, COLOR_BTN_BLUE_SHADE))
            
            items.append(ft.Container(height=10))
            items.append(ft.Row([
                create_safe_btn("LỊCH SỬ", view_history, COLOR_BTN_GREY, COLOR_BTN_GREY_SHADE),
                create_safe_btn("CÀI ĐẶT", goto_settings, COLOR_BTN_GREY, COLOR_BTN_GREY_SHADE),
                create_safe_btn("RESET", reset_game, COLOR_BTN_GREY, COLOR_BTN_GREY_SHADE),
            ], spacing=8))
            
            items.append(ft.Container(height=30)) # Padding bottom

            # Dùng ListView cho toàn bộ trang -> Chống lỗi layout tuyệt đối
            page.add(ft.SafeArea(
                ft.ListView(
                    controls=items,
                    padding=15,
                    expand=True
                )
            ))
            page.update()

        # --- MÀN HÌNH CHỌN ---
        def goto_selector(title, items, callback, multi=False):
            page.clean()
            controls = [
                ft.Container(content=ft.Text(title, size=20, weight="bold", color=COLOR_TEXT), padding=20, alignment=ft.Alignment(0,0))
            ]
            if not multi:
                for p in items:
                    controls.append(create_safe_btn(p["name"], lambda e, x=p: callback(x), COLOR_BTN_BLUE, COLOR_BTN_BLUE_SHADE))
                    controls.append(ft.Container(height=10))
            else:
                checks = []
                for p in items:
                    cb = ft.Checkbox(label=p["name"], fill_color=COLOR_BTN_BLUE)
                    checks.append({"cb": cb, "val": p})
                    controls.append(ft.Container(content=cb, padding=10, bgcolor="white", border_radius=8, border=ft.border.all(1, "#BDC3C7")))
                    controls.append(ft.Container(height=5))
                def submit(e): callback([x["val"] for x in checks if x["cb"].value])
                controls.append(ft.Container(height=10))
                controls.append(create_safe_btn("XÁC NHẬN", submit, "#27AE60", "#1E8449"))
            
            controls.append(ft.Container(height=10))
            controls.append(ft.TextButton("Quay lại", on_click=lambda e: (callback(None) if not multi else callback([]))))
            page.add(ft.SafeArea(ft.ListView(controls=controls, padding=20, expand=True)))
            page.update()

        # --- LOGIC (GIỮ NGUYÊN) ---
        def on_nop_ga_auto(p):
            if not p: return view_dashboard()
            count = sum(1 for log in state["current_logs"] if log.startswith(f"{p['name']}"))
            if count >= 3:
                page.snack_bar = ft.SnackBar(ft.Text("Đã nộp đủ 3 lần!"), bgcolor="red"); page.snack_bar.open=True; page.update(); return view_dashboard()
            
            lan_thu = count + 1
            he_so = 4 if lan_thu == 3 else (2 if lan_thu == 2 else 1)
            amt = state["bet"] * he_so
            p["money"] -= amt; state["pot"] += amt
            state["current_logs"].append(f"{p['name']} bị ăn cây {lan_thu}: -{int(amt)}k (Gà +{int(amt)}k)")
            view_dashboard()

        def on_nhat_selected(nhat):
            if not nhat: return view_dashboard()
            temp_data.clear(); temp_data["nhat"] = nhat
            goto_selector("AI BỊ MÓM?", [p for p in state["players"] if p != nhat], on_mom_selected, multi=True)

        def on_mom_selected(moms):
            temp_data["moms"] = moms
            normals = [p for p in state["players"] if p != temp_data["nhat"] and p not in moms]
            if len(normals) <= 1: 
                if len(normals) == 1: temp_data["nhi"] = normals[0]
                finalize_rank()
            else: goto_selector("AI VỀ NHÌ?", normals, on_nhi_selected)

        def on_nhi_selected(nhi):
            if not nhi: return finalize_rank()
            temp_data["nhi"] = nhi
            remaining = [p for p in state["players"] if p not in [temp_data["nhat"], nhi] + temp_data["moms"]]
            if len(remaining) > 1: goto_selector("AI VỀ BA?", remaining, on_ba_selected)
            else: finalize_rank()

        def on_ba_selected(ba):
            if ba: temp_data["ba"] = ba
            finalize_rank()

        def finalize_rank():
            nhat, moms = temp_data["nhat"], temp_data["moms"]
            normal_losers = []
            if "nhi" in temp_data: normal_losers.append(temp_data["nhi"])
            if "ba" in temp_data: normal_losers.append(temp_data["ba"])
            accounted = [nhat] + moms + normal_losers
            normal_losers.extend([p for p in state["players"] if p not in accounted])

            total_win = 0; details = []
            for p in moms:
                amt = state["bet"] * 4; p["money"] -= amt; total_win += amt
                details.append(f"{p['name']} (Móm): -{int(amt)}k")
            for i, p in enumerate(normal_losers):
                amt = state["bet"] * (i + 1); p["money"] -= amt; total_win += amt
                rank = ["Nhì", "Ba", "Bét"][i] if i < 3 else "Bét"
                details.append(f"{p['name']} ({rank}): -{int(amt)}k")
            nhat["money"] += total_win
            details.insert(0, f"{nhat['name']} (Nhất): +{int(total_win)}k")
            commit_log("Tổng kết", details); temp_data.clear(); view_dashboard()

        def on_u_selected(u):
            if not u: return view_dashboard()
            temp_data["u"] = u
            goto_selector("CÓ AI ĐỀN LÀNG?", [p for p in state["players"] if p != u], on_den_selected)

        def on_den_selected(den):
            u = temp_data["u"]; tien = state["bet"] * 5; details = []
            if den:
                phat = tien * 3; den["money"] -= phat; u["money"] += phat
                details.append(f"{den['name']} đền: -{int(phat)}k")
            else:
                for p in state["players"]:
                    if p != u: p["money"] -= tien; u["money"] += tien; details.append(f"{p['name']}: -{int(tien)}k")
            if state["pot"] > 0:
                u["money"] += state["pot"]; details.append(f"Ăn gà: +{int(state['pot'])}k"); state["pot"] = 0
            details.insert(0, f"{u['name']} Ù"); commit_log("Ván Ù", details); view_dashboard()

        def view_history(e):
            page.clean()
            controls = [ft.Text("LỊCH SỬ", size=20, weight="bold", color=COLOR_TEXT)]
            if not state["history"]: controls.append(ft.Text("Trống", color="grey"))
            else:
                for log in state["history"]:
                    txt = "\n".join(log["details"])
                    controls.append(ft.Container(padding=10, bgcolor="white", border_radius=8, border=ft.border.all(1, "#BDC3C7"), content=ft.Column([
                        ft.Row([ft.Text(log["title"], weight="bold"), ft.Text(log["time"], color="grey")], alignment="spaceBetween"),
                        ft.Text(txt, size=12)
                    ])))
                    controls.append(ft.Container(height=5))
            controls.append(ft.Container(height=10))
            controls.append(create_safe_btn("QUAY LẠI", lambda e: view_dashboard(), COLOR_BTN_GREY, COLOR_BTN_GREY_SHADE))
            page.add(ft.SafeArea(ft.ListView(controls=controls, padding=20, expand=True)))
            page.update()

        def goto_rename(p):
            page.clean()
            tf = ft.TextField(value=p["name"], text_align="center")
            page.add(ft.SafeArea(ft.Container(content=ft.Column([ft.Text("ĐỔI TÊN", size=20), tf, create_safe_btn("LƯU", lambda e: (setattr(p, 'name', tf.value.strip()) or True) and view_dashboard() if tf.value else None, "#27AE60", "#1E8449")], spacing=20), padding=30)))
            page.update()

        def goto_settings(e):
            page.clean()
            tf = ft.TextField(value=str(int(state["bet"])), keyboard_type="number", text_align="center")
            def save(e):
                try: state["bet"] = float(tf.value)
                except: pass
                view_dashboard()
            page.add(ft.SafeArea(ft.Container(content=ft.Column([ft.Text("MỨC CƯỢC", size=20), tf, create_safe_btn("LƯU", save, "#27AE60", "#1E8449")], spacing=20), padding=30)))
            page.update()

        def reset_game(e):
            for p in state["players"]: p["money"] = 0
            state["pot"] = 0; state["history"] = []; state["current_logs"] = []
            view_dashboard()

        view_dashboard()

    except Exception as e:
        page.clean()
        page.add(ft.SafeArea(ft.Column([
            ft.Text("LỖI:", color="red", size=20),
            ft.Text(str(e)),
            ft.ElevatedButton("Thử lại", on_click=lambda _: page.window_reload())
        ], alignment="center")))
        page.update()

ft.app(target=main)
