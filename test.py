import tkinter as tk
from tkinter import filedialog, messagebox
import os
import datetime
import json
import pandas as pd


class CSVProcessorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("CSV Processor")
        self.configurations = {}
        self.load_configurations()

        # メインフレーム
        self.main_frame = tk.Frame(self.root, padx=10, pady=10)
        self.main_frame.pack(fill="both", expand=True)

        # 設定セクション
        tk.Label(self.main_frame, text="設定メニュー", font=('MS Gothic', 20)).pack(pady=5)
        tk.Label(text = u'ラベル').place(x = 10, y = 10, width = 230, height = 50 )
        tk.Button(self.main_frame, text="新規設定を作成", command=self.create_new_setting).pack(pady=5)
        tk.Button(self.main_frame, text="設定を読み込み", command=self.load_setting).pack(pady=5)

        # 現在の設定表示
        self.current_setting_label = tk.Label(self.main_frame, text="現在の設定: なし", font=("Arial", 12))
        self.current_setting_label.pack(pady=10)

        # 実行ボタン
        tk.Button(self.main_frame, text="CSV処理を開始", command=self.start_processing).pack(pady=5)

    def create_new_setting(self):
      # 新規設定作成ウィンドウ
      setting_window = tk.Toplevel(self.root)
      setting_window.title("新規設定を作成")

      # Mac用フォント設定
      label_font = ("Helvetica", 14)  # ラベル用フォント
      entry_font = ("Helvetica", 12)  # エントリーフィールド用フォント


      def save_setting():
          # 設定保存処理
          setting_name = setting_name_entry.get()
          output_folder = output_folder_var.get()
          csv_name_prefix = csv_name_prefix_entry.get()

          # 先頭カラム設定
          column_settings = {
              "lineno": {"column": lineno_col_entry.get(), "row": lineno_row_entry.get(), "default": lineno_default_entry.get()},
              "partno": {"column": partno_col_entry.get(), "row": partno_row_entry.get(), "default": partno_default_entry.get()},
              "value": {"column": value_col_entry.get(), "row": value_row_entry.get(), "default": value_default_entry.get()},
              "date": {"column": date_col_entry.get(), "row": date_row_entry.get(), "default": date_default_entry.get()},
          }

          # 必須フィールドの確認
          if not setting_name or not output_folder or not csv_name_prefix:
              messagebox.showerror("エラー", "全てのフィールドを入力してください")
              return

          self.configurations[setting_name] = {
              "output_folder": output_folder,
              "csv_name_prefix": csv_name_prefix,
              "column_settings": column_settings,
          }
          self.save_configurations()
          self.current_setting_label.config(text=f"現在の設定: {setting_name}")
          setting_window.destroy()

      # 入力フィールド
      tk.Label(setting_window, text="設定名称", font= ("Helvetica", 12)).pack(pady=5)
      setting_name_entry = tk.Entry(setting_window, width=40)
      setting_name_entry.pack(pady=5)

      tk.Label(setting_window, text="出力フォルダ", font= ("Helvetica", 12)).pack(pady=5)
      output_folder_var = tk.StringVar()
      output_folder_entry = tk.Entry(setting_window, textvariable=output_folder_var, width=40)
      output_folder_entry.pack(pady=5)
      tk.Button(setting_window, text="フォルダ選択", command=lambda: output_folder_var.set(filedialog.askdirectory())).pack(pady=5)

      tk.Label(setting_window, text="CSVファイル名の接頭辞", font= ("Helvetica", 12)).pack(pady=5)
      csv_name_prefix_entry = tk.Entry(setting_window, width=40)
      csv_name_prefix_entry.pack(pady=5)

      tk.Label(setting_window, text="先頭カラム設定 (列, 行, 手動設定値)", font=("Arial", 12)).pack(pady=10)

      # 各カラム設定
      def create_column_input(label_text):
          frame = tk.Frame(setting_window)
          frame.pack(pady=5, anchor="w")
          tk.Label(frame, text=label_text, font=("Arial", 10)).grid(row=0, column=0, padx=5)
          tk.Label(frame, text="列:").grid(row=0, column=1, padx=5)
          col_entry = tk.Entry(frame, width=5)
          col_entry.grid(row=0, column=2, padx=5)
          tk.Label(frame, text="行:").grid(row=0, column=3, padx=5)
          row_entry = tk.Entry(frame, width=5)
          row_entry.grid(row=0, column=4, padx=5)
          tk.Label(frame, text="手動設定値:").grid(row=0, column=5, padx=5)
          default_entry = tk.Entry(frame, width=10)
          default_entry.grid(row=0, column=6, padx=5)
          return col_entry, row_entry, default_entry

      lineno_col_entry, lineno_row_entry, lineno_default_entry = create_column_input("1. lineno")
      partno_col_entry, partno_row_entry, partno_default_entry = create_column_input("2. partno")
      value_col_entry, value_row_entry, value_default_entry = create_column_input("3. value")
      date_col_entry, date_row_entry, date_default_entry = create_column_input("4. date")

      # 保存ボタン
      tk.Button(setting_window, text="保存", command=save_setting).pack(pady=20)
    
    def load_setting(self):
        # 設定読み込みウィンドウ
        setting_window = tk.Toplevel(self.root)
        setting_window.title("設定を読み込み")

        def select_setting():
            selected = settings_listbox.get(settings_listbox.curselection())
            self.current_setting_label.config(text=f"現在の設定: {selected}")
            setting_window.destroy()

        # 設定リスト表示
        tk.Label(setting_window, text="利用可能な設定:", font=("Arial", 12)).pack(pady=5)
        settings_listbox = tk.Listbox(setting_window, height=10, width=50)
        for setting in self.configurations.keys():
            settings_listbox.insert(tk.END, setting)
        settings_listbox.pack(pady=5)
        tk.Button(setting_window, text="選択", command=select_setting).pack(pady=10)

    def start_processing(self):
        # CSV処理開始
        current_setting_name = self.current_setting_label.cget("text").replace("現在の設定: ", "")
        if current_setting_name == "なし":
            messagebox.showerror("エラー", "設定を選択してください")
            return

        setting = self.configurations[current_setting_name]
        output_folder = setting["output_folder"]
        csv_name_prefix = setting["csv_name_prefix"]

        if not os.path.exists(output_folder):
            messagebox.showerror("エラー", "出力フォルダが存在しません")
            return

        # ダミーのCSV処理
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = os.path.join(output_folder, f"{csv_name_prefix}_{timestamp}.csv")
        dummy_data = {"lineno": [1], "partno": [2], "value": [3], "date": ["2024-11-20"]}
        df = pd.DataFrame(dummy_data)
        df.to_csv(output_file, index=False)
        messagebox.showinfo("完了", f"CSVファイルを出力しました: {output_file}")

    def save_configurations(self):
        # 設定をJSONファイルに保存
        with open("configurations.json", "w") as f:
            json.dump(self.configurations, f)

    def load_configurations(self):
        # JSONファイルから設定を読み込み
        if os.path.exists("configurations.json"):
            with open("configurations.json", "r") as f:
                self.configurations = json.load(f)


if __name__ == "__main__":
    root = tk.Tk()
    app = CSVProcessorApp(root)
    root.mainloop()
