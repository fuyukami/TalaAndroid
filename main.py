import flet as ft
from datetime import datetime
import logging

# --- CẤU HÌNH ---
logging.basicConfig(level=logging.INFO)

# Bảng màu
COLOR_BG = "#F2F2F2"          
COLOR_HEADER = "#1F2937"
COLOR_TEXT = "#333333"   
COLOR_GOLD = "#F1C40F"        

DEF_BET = 10
PLAYERS_DEF = ["Người 1", "Người 2", "Người 3", "Người 4"]

def main(page: ft.Page):
    try:
        # 1. CẤU HÌNH TRANG CƠ BẢN (AN TOÀN NHẤT)
        page.title = "TÁ LẢ PRO"
        page.theme_mode = ft.ThemeMode.LIGHT
        page.bgcolor = COLOR_BG
        # Tự động cuộn trang (Thay vì dùng ListView)
        page.scroll = ft.ScrollMode.AUTO 
        # Padding trên 30 để tránh tai thỏ (Thay vì SafeArea)
        page.padding = ft.padding.only(top=30, left=10, right=10, bottom=10)

        # --- BIẾN TOÀN CỤC ---
        state = {
            "bet": DEF_BET,
            "pot": 0,
            "players": [{"name": n, "money": 0} for n in PLAYERS_DEF],
            "history": [],      
            "current_logs": []
        }
        temp_data = {}

        # --- HÀM TẠO NÚT CHUẨN (KHÔNG DÙNG CONTAINER) ---
        def create_btn(text, action, bg_color, color="white"):
            return ft.ElevatedButton(
                text=text,
                on_click=action,
                bgcolor=bg_color,
                color=color,
                style=ft.ButtonStyle(
                    shape=ft.RoundedRectangleBorder(radius=8),
                    padding=15,
                ),
                height=50,
                width=1000 # Full width
            )

        # --- THẺ NGƯỜI CHƠI ---
        def create_player_card(p):
            money = int(p['money'])
            money_color = "green" if money >= 0 else "red"
            
            return ft.Card(
                elevation=2, # Đổ bóng nhẹ chuẩn Android
                color="white",
                content=ft.Container(
                    padding=15,
                    content=ft.Row([
                        ft.Row([
                            ft.Icon(ft.icons.PERSON, size=30, color="#555555"),
                            ft.Column([
                                ft.Text(p["name"], weight="bold", size=16, color="#333333"),
                                ft.GestureDetector(
                                    content=ft.Text("Sửa tên", size=12, color="blue"),
                                    on_tap=lambda e: goto_rename(p)
                                )
                            ], spacing=2),
                        ]),
                        ft.Text(f"{money:,} k", color=money_color, weight="bold", size=18),
                    ], alignment="spaceBetween")
                )
            )

        # --- GHI LOG ---
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

        # --- MÀN HÌNH CHÍNH ---
        def view_dashboard():
            page.clean()

            # 1. HEADER
            header = ft.Container(
                bgcolor=COLOR_HEADER,
                padding=20,
                border_radius=10,
                content=ft.Row([
                    ft.Column([
                        ft.Text("MỨC CƯỢC", size=12, color="#AAAAAA"),
                        ft.Text(f"{int(state['bet']):,} K", size=24, weight="bold", color="white")
                    ], horizontal_alignment="center", expand=True),
                    ft.Container(width=1, height=40, bgcolor="#555555"),
                    ft.Column([
                        ft.Text("QUỸ GÀ", size=12, color=COLOR_GOLD),
                        ft.Text(f"{int(state['pot']):,} K", size=30, weight="bold", color=COLOR_GOLD)
                    ], horizontal_alignment="center", expand=True),
                ])
            )

            # 2. DANH SÁCH NGƯỜI CHƠI
            page.add(header)
            page.add(ft.Container(height=10)) # Khoảng cách
            
            for p in state["players"]:
                page.add(create_player_card(p))

            # 3. NÚT CHỨC NĂNG
            page.add(ft.Container(height=20))
            
            page.add(ft.Row([
                ft.Expanded(create_btn("NỘP GÀ", lambda e: goto_selector("AI BỊ ĂN?", state["players"], on_nop_ga_auto), "#F39C12")),
                ft.Container(width=10),
                ft.Expanded(create_btn("XỬ LÝ Ù", lambda e: goto_selector("AI Ù?", state["players"], on_u_selected), "#E74C3C")),
            ]))
            
            page.add(ft.Container(height=10))
            page.add(create_btn("XẾP HẠNG VÁN ĐẤU", lambda e: goto_selector("AI VỀ NHẤT?", state["players"], on_nhat_selected), "#3498DB"))
            
            page.add(ft.Container(height=10))
            page.add(ft.Row([
                ft.Expanded(create_btn("LỊCH SỬ", view_history, "#95A5A6")),
                ft.Container(width=5),
                ft.Expanded(create_btn("CÀI ĐẶT", goto_settings, "#95A5A6")),
                ft.Container(width=5),
                ft.Expanded(create_btn("RESET", reset_game, "#95A5A6")),
            ]))
            
            # Thêm khoảng trống cuối trang để vuốt cho dễ
            page.add(ft.Container(height=50))
            page.update()

        # --- MÀN HÌNH CHỌN ---
        def goto_selector(title, items, callback, multi=False):
            page.clean()
            page.add(ft.Text(title, size=22, weight="bold", color="#333333"))
            page.add(ft.Container(height=20))
            
            if not multi:
                for p in items:
                    page.add(create_btn(p["name"], lambda e, x=p: callback(x), "#3498DB"))
                    page.add(ft.Container(height=10))
            else:
                checks = []
                for p in items:
                    cb = ft.Checkbox(label=p["name"])
                    checks.append({"cb": cb, "val": p})
                    page.add(ft.Container(content=cb, bgcolor="white", padding=10, border_radius=5))
                    page.add(ft.Container(height=5))
                
                def submit(e): callback([x["val"] for x in checks if x["cb"].value])
                page.add(ft.Container(height=10))
                page.add(create_btn("XÁC NHẬN", submit, "#2ECC71"))
            
            page.add(ft.Container(height=20))
            page.add(ft.TextButton("Quay lại", on_click=lambda e: (callback(None) if not multi else callback([]))))
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
            page.add(ft.Text("LỊCH SỬ", size=22, weight="bold"))
            if not state["history"]: page.add(ft.Text("Trống", color="grey"))
            else:
                for log in state["history"]:
                    txt = "\n".join(log["details"])
                    page.add(ft.Container(
                        padding=15, bgcolor="white", border_radius=5, 
                        content=ft.Column([
                            ft.Row([ft.Text(log["title"], weight="bold"), ft.Text(log["time"], color="grey")], alignment="spaceBetween"),
                            ft.Text(txt, size=14)
                        ])
                    ))
                    page.add(ft.Container(height=5))
            page.add(ft.Container(height=10))
            page.add(create_btn("QUAY LẠI", lambda e: view_dashboard(), "#95A5A6"))
            page.update()

        def goto_rename(p):
            page.clean()
            tf = ft.TextField(value=p["name"], text_align="center")
            page.add(ft.Text("ĐỔI TÊN", size=22))
            page.add(tf)
            page.add(ft.Container(height=20))
            page.add(create_btn("LƯU", lambda e: (setattr(p, 'name', tf.value.strip()) or True) and view_dashboard() if tf.value else None, "#2ECC71"))
            page.update()

        def goto_settings(e):
            page.clean()
            tf = ft.TextField(value=str(int(state["bet"])), keyboard_type="number", text_align="center")
            def save(e):
                try: state["bet"] = float(tf.value)
                except: pass
                view_dashboard()
            page.add(ft.Text("CÀI ĐẶT", size=22))
            page.add(tf)
            page.add(ft.Container(height=20))
            page.add(create_btn("LƯU", save, "#2ECC71"))
            page.update()

        def reset_game(e):
            for p in state["players"]: p["money"] = 0
            state["pot"] = 0; state["history"] = []; state["current_logs"] = []
            view_dashboard()

        view_dashboard()

    except Exception as e:
        page.add(ft.Text(f"LỖI: {str(e)}", color="red"))
        page.update()

ft.app(target=main)
