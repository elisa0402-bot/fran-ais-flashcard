"""On y va: native Windows flashcards. No web browser or web view."""
from __future__ import annotations
import argparse, base64, csv, hashlib, io, json, os, shutil, subprocess, sys
import threading, time, unicodedata, urllib.request, zlib
from datetime import datetime, timezone, timedelta
from pathlib import Path
import tkinter as tk
from tkinter import ttk, messagebox, filedialog

TITLE = "On y va · 뉴스 프랑스어"
RAW_URL = "https://raw.githubusercontent.com/elisa0402-bot/fran-ais-flashcard/main/news/data.json"
DAY = 86400000
SEED_B64 = "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"
def physical_path(path):
    """Keep installed shortcuts usable outside a packaged parent process."""
    path = Path(path).resolve()
    if os.name != "nt" or not path.is_file(): return path
    import ctypes, msvcrt
    from ctypes import wintypes
    api = ctypes.WinDLL("kernel32", use_last_error=True).GetFinalPathNameByHandleW
    api.argtypes = [wintypes.HANDLE, wintypes.LPWSTR, wintypes.DWORD, wintypes.DWORD]
    api.restype = wintypes.DWORD
    buffer = ctypes.create_unicode_buffer(32768)
    with path.open("rb") as stream:
        size = api(msvcrt.get_osfhandle(stream.fileno()), buffer, len(buffer), 0)
    if not size or size >= len(buffer): raise OSError("설치 경로를 확인하지 못했습니다.")
    value = buffer.value
    if value.startswith("\\\\?\\UNC\\"): value = "\\\\" + value[8:]
    elif value.startswith("\\\\?\\"): value = value[4:]
    return Path(value)

APP_FILE = physical_path(__file__)
HOME = (APP_FILE.parent.parent if APP_FILE.parent.name == "App" and APP_FILE.parent.parent.name == "OnYVaCarnet"
        else Path(os.environ.get("LOCALAPPDATA", str(Path.home()))) / "OnYVaCarnet")
INK, PAPER, MINT, MUTED = "#183d35", "#faf9f5", "#e9f0e6", "#75816d"
HIDDEN = getattr(subprocess, "CREATE_NO_WINDOW", 0)

def now_ms():
    return int(time.time() * 1000)

def day_key(ms):
    return datetime.fromtimestamp(ms / 1000, timezone(timedelta(hours=9))).strftime("%Y-%m-%d")

def normalize(text):
    return " ".join(unicodedata.normalize("NFKC", text).casefold().replace("’", "'").replace("‘", "'").split())

def embedded():
    data = json.loads(zlib.decompress(base64.b64decode(SEED_B64)))
    validate(data["cards"])
    return data

def validate(cards):
    if not isinstance(cards, list) or len(cards) > 20000:
        raise ValueError("단어 목록 형식이 올바르지 않습니다.")
    ids, words = set(), set()
    for c in cards:
        if not isinstance(c, dict) or not all(isinstance(c.get(k), str) and c[k].strip() for k in ("id", "fr", "ko")):
            raise ValueError("표현이나 뜻이 비어 있습니다.")
        if c["id"] in ids or normalize(c["fr"]) in words:
            raise ValueError("같은 번호나 표현이 중복되어 있습니다.")
        ids.add(c["id"]); words.add(normalize(c["fr"]))
        if not isinstance(c.get("examples"), list) or not all(isinstance(e, dict) and isinstance(e.get("fr"), str) and isinstance(e.get("ko"), str) for e in c["examples"]):
            raise ValueError("예문 형식이 올바르지 않습니다.")
        if "dates" in c and not isinstance(c["dates"], list):
            raise ValueError("날짜 목록이 올바르지 않습니다.")

def empty_state():
    return dict(schemaVersion=1, cards=[], progress={}, stars=[], settings=dict(newPerDay=10, speechRate=.9), activity=[], lastSync=0, updated="")

def merge(state, cards):
    validate(cards)
    by_word = {normalize(c["fr"]): c for c in state["cards"]}
    ids = {c["id"] for c in state["cards"]}
    added = 0
    for incoming in cards:
        c = json.loads(json.dumps(incoming, ensure_ascii=False))
        prior = by_word.get(normalize(c["fr"]))
        if prior:
            prior["dates"] = sorted(set(prior.get("dates", []) + c.get("dates", [])))
            if prior.get("deck") == c.get("deck") == "news":
                prior["ko"], prior["examples"] = c["ko"], c["examples"]
        else:
            if c["id"] in ids:
                raise ValueError("다른 표현에 같은 번호가 있습니다.")
            ids.add(c["id"]); by_word[normalize(c["fr"])] = c
            state["cards"].append(c); added += 1
    return added

def grade(old, rating, now):
    p = dict(due=0, reps=0, interval=0, ease=2.5, lapses=0, seen=False, successes=0)
    p.update(old or {}); p.update(seen=True, last=now)
    if rating == "again":
        p.update(interval=0, reps=0, lapses=p["lapses"]+1, successes=0, ease=max(1.3, p["ease"]-.2), due=now+60000)
    elif rating == "hard":
        p.update(interval=0, ease=max(1.3, p["ease"]-.1), due=now+600000)
    elif rating in ("good", "easy"):
        easy = rating == "easy"
        interval = (4 if easy else 1) if p["reps"] == 0 else (7 if easy else 3) if p["reps"] == 1 else max(p["interval"]+1, int(p["interval"]*p["ease"]*(1.3 if easy else 1)+.5))
        p.update(interval=interval, reps=p["reps"]+1, successes=p["successes"]+1, ease=min(3.3, p["ease"]+(.15 if easy else 0)), due=now+min(365, interval)*DAY)
    else:
        raise ValueError("잘못된 평가")
    return p

def unlocked(state, c):
    return state["progress"].get(c["id"]+":fr", {}).get("successes", 0) >= 2

def learned(state, c):
    return all(state["progress"].get(c["id"]+":"+d, {}).get("interval", 0) >= 7 for d in ("fr", "ko"))

def queue(state, now, mode="auto"):
    used = {a["id"] for a in state["activity"] if a.get("newWord") and day_key(a["time"]) == day_key(now)}
    remaining = max(0, state["settings"]["newPerDay"] - len(used))
    due, fresh = [], []
    for c in state["cards"]:
        if mode != "ko":
            p = state["progress"].get(c["id"]+":fr", {})
            if not p.get("seen"): fresh.append((c, "fr", 0))
            elif p["due"] <= now: due.append((c, "fr", p["due"]))
        if mode != "fr" and unlocked(state, c):
            p = state["progress"].get(c["id"]+":ko", {})
            if not p.get("seen") or p["due"] <= now: due.append((c, "ko", p.get("due", 0)))
    fresh.sort(key=lambda x: (x[0].get("added", ""), x[0]["fr"]), reverse=True)
    return sorted(due, key=lambda x: x[2]) + fresh[:remaining]

def atomic_write(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_suffix(path.suffix+".tmp")
    temp.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    if path.exists(): shutil.copy2(path, str(path)+".previous")
    os.replace(temp, path)

def clean_state(state):
    if state.get("schemaVersion") != 1: raise ValueError("알 수 없는 기록 형식")
    validate(state["cards"])
    for k, default in empty_state().items(): state.setdefault(k, default)
    if not isinstance(state["progress"], dict) or not isinstance(state["activity"], list): raise ValueError("진도 형식 오류")
    state["settings"]["newPerDay"] = max(1, min(100, int(state["settings"].get("newPerDay", 10))))
    known = {c["id"] for c in state["cards"]}
    for key, p in list(state["progress"].items()):
        if key[:-3] not in known or key[-3:] not in (":fr", ":ko") or not isinstance(p, dict):
            del state["progress"][key]; continue
        for field in ("due", "reps", "interval", "ease", "lapses", "successes"):
            value = p.get(field, 0)
            if not isinstance(value, (int, float)) or not 0 <= value < 1e16: raise ValueError("진도 수치 오류")
    return state

class Store:
    def __init__(self, folder):
        self.folder, self.warning = Path(folder), None
        self.path = self.folder/"progress.json"
        self.state = empty_state()
        if self.path.exists():
            try: self.state = clean_state(json.loads(self.path.read_text(encoding="utf-8-sig")))
            except Exception as e:
                self.warning = "기존 진도를 읽지 못했습니다. 원본을 보관하고 새로 시작합니다.\n"+str(e)
                shutil.copy2(self.path, str(self.path)+".unreadable-"+str(now_ms()))
        seed = embedded()
        merge(self.state, seed["cards"])
        self.state["updated"] = max(self.state.get("updated", ""), seed["updated"])
    def save(self):
        atomic_write(self.path, self.state)

def ps_quote(value):
    return "'"+str(value).replace("'", "''")+"'"

def install():
    source = APP_FILE
    target = HOME/"App"
    target.mkdir(parents=True, exist_ok=True)
    for name in ("OnYVaCarnet.pyw", "icon.ico", "data.json"):
        src, dst = source.parent/name, target/name
        if src.exists() and src.resolve() != dst.resolve(): shutil.copy2(src, dst)
    bundled = source.parent/"runtime"
    installed_runtime = target/"runtime"
    if (bundled/"pythonw.exe").exists() and bundled.resolve() != installed_runtime.resolve():
        shutil.copytree(bundled, installed_runtime, dirs_exist_ok=True)
    target = physical_path(target/"OnYVaCarnet.pyw").parent
    installed_runtime = target/"runtime"
    pythonw = installed_runtime/"pythonw.exe" if (installed_runtime/"pythonw.exe").exists() else Path(sys.executable).with_name("pythonw.exe")
    if not pythonw.exists(): raise RuntimeError("앱 실행 환경을 찾지 못했습니다.")
    script = "$shell=New-Object -ComObject WScript.Shell;$desktop=[Environment]::GetFolderPath('Desktop');$link=$shell.CreateShortcut((Join-Path $desktop '프랑스어 뉴스 단어장.lnk'));$link.TargetPath="+ps_quote(pythonw)+";$link.Arguments="+ps_quote('"'+str(target/"OnYVaCarnet.pyw")+'"')+";$link.WorkingDirectory="+ps_quote(target)+";$link.Description='On y va - 뉴스 프랑스어';$link.IconLocation="+ps_quote(str(target/"icon.ico"))+";$link.Save();"
    result = subprocess.run(["powershell.exe","-NoProfile","-NonInteractive","-WindowStyle","Hidden","-Command",script], capture_output=True, creationflags=HIDDEN)
    if result.returncode: raise RuntimeError(result.stderr.decode("utf-8", errors="replace"))
    return target/"OnYVaCarnet.pyw"

class App:
    def __init__(self, root, folder, preview=False):
        self.root, self.store, self.preview = root, Store(folder), preview
        self.current, self.revealed, self.syncing = None, False, False
        root.title(TITLE); root.geometry("1120x900"); root.minsize(950,760); root.configure(bg=PAPER)
        try: root.iconbitmap(str(Path(__file__).with_name("icon.ico")))
        except Exception: pass
        self.style = ttk.Style(root); self.style.theme_use("clam")
        self.style.configure(".", font=("Malgun Gothic",10), background=PAPER, foreground=INK)
        self.style.configure("TNotebook", background=PAPER, borderwidth=0)
        self.style.configure("TNotebook.Tab", padding=(20,10))
        self.style.configure("TButton", padding=(12,9), background=MINT, foreground=INK)
        self.style.configure("Primary.TButton", background=INK, foreground="white")
        self.style.map("Primary.TButton", background=[("active","#2e5e4c")], foreground=[("active","white")])
        self.style.configure("Treeview", rowheight=43, background="white", fieldbackground="white", font=("Malgun Gothic",10))
        self.style.configure("Treeview.Heading", padding=(8,9), background=MINT)
        self.style.map("Treeview", background=[("selected","#dce8d2")], foreground=[("selected",INK)])
        header = tk.Frame(root, bg=PAPER); header.pack(fill="x", padx=30, pady=(20,15))
        logo = tk.Frame(header,bg=PAPER);logo.pack(side="left")
        tk.Label(logo,text="On y va",font=("Georgia",28,"italic"),bg=PAPER,fg=INK).pack(anchor="w")
        tk.Label(logo,text="나의 뉴스 프랑스어 · 전용 Windows 창",font=("Malgun Gothic",9),bg=PAPER,fg=MUTED).pack(anchor="w")
        for text,command in (("바탕화면에 설치",self.install_click),("진도 백업",self.backup),("새 어휘 확인",lambda:self.sync(True))):
            ttk.Button(header,text=text,command=command).pack(side="right",padx=5)
        self.status = tk.StringVar(value="오프라인에서도 "+str(len(self.s["cards"]))+"개 표현으로 학습할 수 있습니다.")
        tk.Label(root,textvariable=self.status,bg=PAPER,fg=MUTED,anchor="w",font=("Malgun Gothic",9)).pack(side="bottom",fill="x",padx=30,pady=10)
        self.tabs = ttk.Notebook(root);self.tabs.pack(fill="both",expand=True,padx=28)
        self.study,self.library,self.settings = (tk.Frame(self.tabs,bg=PAPER) for _ in range(3))
        for frame,title in ((self.study,"오늘의 복습"),(self.library,"전체 단어"),(self.settings,"설정과 백업")):self.tabs.add(frame,text=title)
        self.build_study();self.build_library();self.build_settings()
        self.tabs.bind("<<NotebookTabChanged>>",self.tab_changed)
        root.bind("<Key>",self.key);root.protocol("WM_DELETE_WINDOW",self.close)
        self.next()
        if self.store.warning:root.after(200,lambda:messagebox.showwarning(TITLE,self.store.warning,parent=root))
        if not preview:root.after(700,self.sync)
        root.after(30000,self.tick)
    @property
    def s(self):return self.store.state
    def label(self,parent,text,size=11,color=INK,**kw):
        return tk.Label(parent,text=text,font=("Malgun Gothic",size),fg=color,bg=parent["bg"],**kw)
    def build_study(self):
        self.counts = self.label(self.study,"",14,anchor="w");self.counts.pack(fill="x",padx=24,pady=(22,16))
        bar = tk.Frame(self.study,bg=PAPER);bar.pack(fill="x",padx=24,pady=(0,12))
        self.session=self.label(bar,"",10,MUTED);self.session.pack(side="left")
        self.direction=ttk.Combobox(bar,state="readonly",width=29,values=["자동 · 이해한 뒤 말하기","프랑스어 → 한국어","한국어 → 프랑스어"])
        self.direction.current(0);self.direction.pack(side="right");self.direction.bind("<<ComboboxSelected>>",lambda _:self.next())
        self.grades=tk.Frame(self.study,bg=PAPER);self.grades.pack(side="bottom",fill="x",padx=18,pady=10)
        self.grade_buttons={}
        for i,(key,text) in enumerate((("again","다시"),("hard","어려워요"),("good","알겠어요"),("easy","쉬워요"))):
            self.grades.columnconfigure(i,weight=1)
            b=ttk.Button(self.grades,text=text,command=lambda k=key:self.grade_click(k),style="Primary.TButton" if key=="good" else "TButton")
            b.grid(row=0,column=i,sticky="ew",padx=5);self.grade_buttons[key]=b
        self.label(self.study,"Space 정답 보기 · 1 다시 · 2 어려워요 · 3 알겠어요 · 4 쉬워요",9,MUTED).pack(side="bottom",pady=5)
        holder=tk.Frame(self.study,bg="white",highlightbackground="#e1e5db",highlightthickness=1);holder.pack(fill="both",expand=True,padx=24,pady=5)
        self.canvas=tk.Canvas(holder,bg="white",highlightthickness=0);scroll=ttk.Scrollbar(holder,orient="vertical",command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=scroll.set);scroll.pack(side="right",fill="y");self.canvas.pack(side="left",fill="both",expand=True)
        self.card=tk.Frame(self.canvas,bg="white",padx=30,pady=24);self.card_window=self.canvas.create_window(0,0,anchor="nw",window=self.card)
        self.card.bind("<Configure>",lambda _:self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        self.canvas.bind("<Configure>",self.resize_card)
        self.canvas.bind_all("<MouseWheel>",self.wheel)
    def resize_card(self,event):
        self.canvas.itemconfigure(self.card_window,width=event.width)
        for child in self.card.winfo_children():
            if isinstance(child,tk.Label):child.configure(wraplength=max(400,event.width-90))
    def wheel(self,event):
        if self.tabs.index("current")==0 and self.canvas.winfo_containing(event.x_root,event.y_root):
            self.canvas.yview_scroll(int(-event.delta/120),"units")
    def stats(self):
        self.counts.configure(text="모은 표현  "+str(len(self.s["cards"]))+"개           지금 학습할 카드  "+str(len(queue(self.s,now_ms())))+"개           익숙해진 표현  "+str(sum(learned(self.s,c) for c in self.s["cards"]))+"개")
        done=sum(day_key(a["time"])==day_key(now_ms()) for a in self.s["activity"])
        self.session.configure(text="오늘 "+str(done)+"회 복습했어요" if done else "하루 "+str(self.s["settings"]["newPerDay"])+"개의 새 표현")
    def mode(self):return ("auto","fr","ko")[self.direction.current()]
    def next(self):
        self.current=next(iter(queue(self.s,now_ms(),self.mode())),None);self.revealed=False;self.stats();self.render()
    def card_text(self,text,size=12,color=INK,font=None,pady=(7,10)):
        label=tk.Label(self.card,text=text,font=font or ("Malgun Gothic",size),bg="white",fg=color,anchor="w",justify="left",wraplength=max(400,self.canvas.winfo_width()-90))
        label.pack(fill="x",pady=pady);return label
    def render(self):
        for w in self.card.winfo_children():w.destroy()
        for key,b in self.grade_buttons.items():b.state(["disabled"]);b.configure(text={"again":"다시","hard":"어려워요","good":"알겠어요","easy":"쉬워요"}[key])
        if not self.current:
            locked=self.mode()=="ko" and not any(unlocked(self.s,c) for c in self.s["cards"])
            self.card_text("먼저 뜻을 익혀볼까요?" if locked else "지금 할 복습을 마쳤어요.",22,pady=(30,20))
            self.card_text("프랑스어→한국어에서 같은 표현을 두 번 기억하면 한국어→프랑스어 카드가 열립니다." if locked else "짧은 재학습은 1분 또는 10분 뒤 다시 열립니다.\n새 표현 수는 설정에서 바꿀 수 있어요.",11,MUTED);return
        c,di,_=self.current
        self.card_text("COMPRENDRE · 프랑스어 → 한국어" if di=="fr" else "S'EXPRIMER · 한국어 → 프랑스어",10,MUTED)
        self.card_text("이 표현의 뜻을 떠올려 보세요." if di=="fr" else "프랑스어로 어떻게 말할까요?",10,MUTED,pady=(15,8))
        self.card_text(c["fr"] if di=="fr" else c["ko"],font=("Georgia",27) if di=="fr" else ("Malgun Gothic",22))
        ttk.Button(self.card,text="프랑스어 듣기 ♫",command=lambda:self.speak(c["fr"])).pack(anchor="w",pady=(5,12))
        if self.revealed:
            self.card_text(c["ko"] if di=="fr" else c["fr"],font=("Malgun Gothic",17) if di=="fr" else ("Georgia",20),pady=(15,20))
            for example in c["examples"]:
                self.card_text(example["fr"],font=("Georgia",16),color="#335942")
                self.card_text(example["ko"],11,MUTED,pady=(0,8))
                ttk.Button(self.card,text="예문 듣기",command=lambda e=example:self.speak(e["fr"])).pack(anchor="w",pady=(0,8))
            self.card_text(c.get("source","나의 표현")+" · "+", ".join(c.get("dates",[])),9,MUTED,pady=(20,8))
            for key,b in self.grade_buttons.items():
                due=grade(self.s["progress"].get(c["id"]+":"+di),key,now_ms())["due"]-now_ms()
                interval=str(max(1,round(due/60000)))+"분 후" if due<3600000 else str(round(due/DAY))+"일 후"
                b.configure(text={"again":"다시","hard":"어려워요","good":"알겠어요","easy":"쉬워요"}[key]+" · "+interval);b.state(["!disabled"])
        else:ttk.Button(self.card,text="정답 보기   Space",style="Primary.TButton",command=self.reveal).pack(fill="x",pady=(20,12))
        self.canvas.yview_moveto(0)
    def reveal(self):
        if self.current and not self.revealed:self.revealed=True;self.render()
    def grade_click(self,rating):
        if not self.current or not self.revealed:return
        c,di,_=self.current;key=c["id"]+":"+di;old=self.s["progress"].get(key);now=now_ms()
        self.s["progress"][key]=grade(old,rating,now)
        self.s["activity"].append(dict(id=c["id"],dir=di,rating=rating,time=now,newWord=di=="fr" and not (old or {}).get("seen")))
        self.s["activity"]=self.s["activity"][-10000:];self.save();self.next()
    def key(self,event):
        if self.tabs.index("current")!=0 or isinstance(self.root.focus_get(),(tk.Entry,tk.Text,ttk.Entry,ttk.Combobox,ttk.Spinbox)):return
        if event.keysym=="space":self.reveal();return "break"
        if self.revealed and event.char in ("1","2","3","4"):self.grade_click(("again","hard","good","easy")[int(event.char)-1]);return "break"
    def save(self):
        try:self.store.save()
        except Exception as e:messagebox.showwarning(TITLE,"진도를 저장하지 못했습니다. 백업 버튼으로 기록을 보관해 주세요.\n"+str(e),parent=self.root)
    def build_library(self):
        bar=tk.Frame(self.library,bg=PAPER);bar.pack(fill="x",padx=20,pady=15)
        self.label(bar,"프랑스어·한국어·예문 검색",10,MUTED).pack(side="left",padx=(0,14))
        self.query=tk.StringVar();ttk.Entry(bar,textvariable=self.query).pack(side="left",fill="x",expand=True)
        self.query.trace_add("write",lambda *_:self.render_library())
        ttk.Button(bar,text="+ 표현 추가",command=self.add_word).pack(side="right",padx=(10,0))
        self.list_count=self.label(self.library,"",10,MUTED);self.list_count.pack(fill="x",padx=20,pady=(0,8))
        body=tk.Frame(self.library,bg=PAPER);body.pack(fill="both",expand=True,padx=20)
        self.tree=ttk.Treeview(body,columns=("fr","ko","date"),show="headings",selectmode="browse")
        for name,heading,width in (("fr","프랑스어",380),("ko","한국어",350),("date","날짜",110)):
            self.tree.heading(name,text=heading);self.tree.column(name,width=width,minwidth=80)
        scrollbar=ttk.Scrollbar(body,orient="vertical",command=self.tree.yview);self.tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right",fill="y");self.tree.pack(side="left",fill="both",expand=True)
        self.library_example=tk.Text(self.library,height=7,wrap="word",font=("Malgun Gothic",11),bg="#eff3e7",fg=INK,relief="flat",padx=15,pady=10,state="disabled")
        self.library_example.pack(fill="x",padx=20,pady=15);self.tree.bind("<<TreeviewSelect>>",self.select_word)
    def render_library(self):
        q=normalize(self.query.get());self.tree.delete(*self.tree.get_children())
        for c in sorted(self.s["cards"],key=lambda c:(c.get("added",""),c["fr"]),reverse=True):
            text=" ".join([c["fr"],c["ko"]]+[e["fr"]+" "+e["ko"] for e in c["examples"]])
            if not q or q in normalize(text):self.tree.insert("","end",iid=c["id"],values=(c["fr"],c["ko"],c.get("added","")))
        self.list_count.configure(text=str(len(self.tree.get_children()))+"개 표현 · 전체 "+str(len(self.s["cards"]))+"개")
    def select_word(self,_=None):
        chosen=self.tree.selection()
        if not chosen:return
        c=next(c for c in self.s["cards"] if c["id"]==chosen[0]);text=c["fr"]+"\n"+c["ko"]+"\n\n"+"\n\n".join(e["fr"]+"\n"+e["ko"] for e in c["examples"])
        self.library_example.configure(state="normal");self.library_example.delete("1.0","end");self.library_example.insert("1.0",text);self.library_example.configure(state="disabled")
    def build_settings(self):
        parent=tk.Frame(self.settings,bg=PAPER,padx=25,pady=20);parent.pack(fill="both",expand=True)
        self.label(parent,"나의 속도로",21).pack(anchor="w",pady=(0,20))
        row=tk.Frame(parent,bg=PAPER);row.pack(fill="x",pady=8)
        self.label(row,"하루 새 표현",11).pack(side="left",padx=(0,20))
        self.limit=tk.StringVar(value=str(self.s["settings"]["newPerDay"]))
        spin=ttk.Spinbox(row,from_=1,to=100,width=7,textvariable=self.limit,command=self.change_limit);spin.pack(side="left")
        spin.bind("<FocusOut>",lambda _:self.change_limit());spin.bind("<Return>",lambda _:self.change_limit())
        info="배운 표현의 복습은 이 숫자에 포함되지 않습니다.\n프→한에서 두 번 기억하면 한→프 카드가 자동으로 열립니다.\n\n인터넷 없이도 실행 파일에 포함된 단어로 학습할 수 있습니다.\n온라인에서는 앱을 열 때와 사용 중 15분마다 새 어휘를 확인합니다.\n학습 기록은 이 컴퓨터에 저장됩니다. 기기를 바꾸기 전에는 백업해 주세요."
        self.label(parent,info,10,MUTED,justify="left",anchor="w").pack(fill="x",pady=20)
        row=tk.Frame(parent,bg=PAPER);row.pack(anchor="w",pady=15)
        for text,cmd in (("진도까지 백업",self.backup),("파일 가져오기",self.import_file),("Anki로 내보내기",self.export_anki)):
            ttk.Button(row,text=text,command=cmd).pack(side="left",padx=(0,10))
        self.label(parent,"매일 오전 9시 어휘 추가는 기존 Codex 자동화가 담당합니다.\nCodex가 실행 가능하고 새 뉴스 브리핑이 있을 때 누적됩니다.\n공식 Anki 앱이나 Anki 계정과는 연결되지 않습니다.",10,MUTED,justify="left").pack(anchor="w",pady=15)
        ttk.Button(parent,text="기록 폴더 열기",command=self.open_data).pack(anchor="w",pady=10)
    def change_limit(self):
        try:self.s["settings"]["newPerDay"]=max(1,min(100,int(self.limit.get())));self.save();self.stats()
        except ValueError:self.limit.set(str(self.s["settings"]["newPerDay"]))
    def tab_changed(self,_=None):
        if not hasattr(self,"tree"):return
        if self.tabs.index("current")==0:self.next()
        elif self.tabs.index("current")==1:self.render_library()
    def backup(self):
        path=filedialog.asksaveasfilename(parent=self.root,title="학습 진도 백업",defaultextension=".json",filetypes=[("단어장 백업","*.json")],initialfile="on-y-va-backup-"+day_key(now_ms())+".json")
        if not path:return
        try:Path(path).write_text(json.dumps(dict(type="onyva-backup",exportedAt=datetime.now(timezone.utc).isoformat(),state=self.s),ensure_ascii=False,indent=2),encoding="utf-8");messagebox.showinfo(TITLE,"진도와 단어를 백업했습니다.",parent=self.root)
        except Exception as e:messagebox.showerror(TITLE,str(e),parent=self.root)
    def import_file(self):
        path=filedialog.askopenfilename(parent=self.root,title="웹·앱 백업 또는 윔피키드 CSV 가져오기",filetypes=[("단어장 파일","*.json *.csv")])
        if not path:return
        try:
            text=Path(path).read_text(encoding="utf-8-sig")
            if Path(path).suffix.lower()==".csv":
                cards=[]
                for i,row in enumerate(csv.reader(io.StringIO(text))):
                    if len(row)<2:continue
                    fr,ko=row[0].strip(),row[1].strip()
                    import re
                    named=re.match(r"^(?:단어|동사|표현|관용구|구문)\s*:\s*(.*)$",fr)
                    if named:fr=named[1]
                    elif re.search("[가-힣]",fr) and re.match("[a-zà-ÿ'’]",ko,re.I):fr,ko=ko,fr
                    ko=re.sub(r"^의미:\s*","",ko)
                    if fr.lower() in ("front","fr","foreign","프랑스어"):continue
                    cards.append(dict(id="import-"+hashlib.sha256(normalize(fr).encode()).hexdigest()[:16],fr=fr,ko=ko,dates=[],added=day_key(now_ms()),deck="personal",source="가져온 CSV",examples=[]))
                # A CSV can contain identical questions: merge them without changing existing progress.
                unique={normalize(c["fr"]):c for c in cards};added=merge(self.s,list(unique.values()))
            else:
                data=json.loads(text)
                if isinstance(data,dict) and data.get("type")=="onyva-backup":
                    incoming=clean_state(data["state"])
                    if not messagebox.askyesno(TITLE,"이 파일의 학습 진도로 복원할까요?\n현재 진도는 기록 폴더에 자동 백업합니다.",parent=self.root):return
                    self.store.folder.mkdir(parents=True,exist_ok=True)
                    (self.store.folder/("before-import-"+str(now_ms())+".json")).write_text(json.dumps(dict(type="onyva-backup",state=self.s),ensure_ascii=False),encoding="utf-8")
                    merge(incoming,self.s["cards"]);self.store.state=incoming;added=0
                    self.limit.set(str(self.s["settings"]["newPerDay"]))
                else:added=merge(self.s,data if isinstance(data,list) else data["cards"])
            self.save();self.next();self.render_library();messagebox.showinfo(TITLE,"가져오기를 마쳤습니다. 새 표현 "+str(added)+"개",parent=self.root)
        except Exception as e:messagebox.showerror(TITLE,"가져오지 못했습니다.\n"+str(e),parent=self.root)
    def export_anki(self):
        path=filedialog.asksaveasfilename(parent=self.root,defaultextension=".tsv",filetypes=[("Anki 텍스트","*.tsv")],initialfile="on-y-va-anki.tsv")
        if not path:return
        from html import escape
        lines=["#separator:tab","#html:true","#columns:Front\tBack\tTags"]
        for c in self.s["cards"]:
            examples="".join("<p>"+escape(e["fr"])+"<br>"+escape(e["ko"])+"</p>" for e in c["examples"])
            lines.append("프→한: "+escape(c["fr"])+"\t"+escape(c["ko"])+examples+"\tonyva-news fr-kr")
            lines.append("한→프: "+escape(c["ko"])+"\t"+escape(c["fr"])+examples+"\tonyva-news kr-fr")
        try:Path(path).write_text("\n".join(lines),encoding="utf-8");messagebox.showinfo(TITLE,"양방향 카드 "+str(len(self.s["cards"])*2)+"개를 내보냈습니다.",parent=self.root)
        except Exception as e:messagebox.showerror(TITLE,str(e),parent=self.root)
    def add_word(self):
        dialog=tk.Toplevel(self.root);dialog.title("나만의 표현 추가");dialog.geometry("570x430");dialog.configure(bg=PAPER);dialog.transient(self.root);dialog.grab_set()
        fields=[]
        for text in ("프랑스어","한국어 뜻","프랑스어 예문","예문 해석"):
            self.label(dialog,text,10).pack(anchor="w",padx=25,pady=(14,5));entry=ttk.Entry(dialog);entry.pack(fill="x",padx=25);fields.append(entry)
        def save_word():
            fr,ko,exfr,exko=[e.get().strip() for e in fields]
            if not all((fr,ko,exfr,exko)):messagebox.showwarning(TITLE,"뜻과 예문을 모두 입력해 주세요.",parent=dialog);return
            c=dict(id="personal-"+hashlib.sha256(normalize(fr).encode()).hexdigest()[:16],fr=fr,ko=ko,dates=[],added=day_key(now_ms()),deck="personal",source="나의 표현",examples=[dict(fr=exfr,ko=exko)])
            merge(self.s,[c]);self.save();self.render_library();self.stats();dialog.destroy()
        ttk.Button(dialog,text="단어장에 저장",style="Primary.TButton",command=save_word).pack(fill="x",padx=25,pady=25)
    def open_data(self):
        self.store.folder.mkdir(parents=True,exist_ok=True);os.startfile(self.store.folder)
    def install_click(self):
        try:
            if self.preview:messagebox.showinfo(TITLE,"점검 모드에서는 설치하지 않습니다.",parent=self.root);return
            installed=install()
            messagebox.showinfo(TITLE,"바탕화면에 ‘프랑스어 뉴스 단어장’을 설치했습니다.\n브라우저나 명령창을 열지 않고 아이콘으로 실행할 수 있습니다.",parent=self.root)
        except Exception as e:messagebox.showerror(TITLE,"설치하지 못했습니다.\n"+str(e),parent=self.root)
    def speak(self,text):
        def work():
            script="$v=New-Object -ComObject SAPI.SpVoice;$voices=@($v.GetVoices() | Where-Object {$_.GetAttribute('Language') -match '(^|;)[0-9a-f]*0c($|;)'});if($voices.Count -eq 0){Write-Output 'NO_FRENCH';exit};$v.Voice=$voices[0];$v.Rate=-1;$v.Speak("+ps_quote(text)+",0)"
            try:
                result=subprocess.run(["powershell.exe","-NoProfile","-NonInteractive","-WindowStyle","Hidden","-Command",script],capture_output=True,creationflags=HIDDEN,timeout=60)
                if result.returncode or b"NO_FRENCH" in result.stdout:self.root.after(0,lambda:messagebox.showinfo(TITLE,"프랑스어 음성을 재생하지 못했습니다. Windows에 프랑스어 음성이 설치되어 있어야 합니다.",parent=self.root))
            except Exception:self.root.after(0,lambda:messagebox.showinfo(TITLE,"음성을 재생하지 못했습니다.",parent=self.root))
        threading.Thread(target=work,daemon=True).start()
    def sync(self,manual=False):
        if self.syncing:return
        self.syncing=True;self.status.set("새 표현을 확인하고 있습니다…")
        def worker():
            try:
                req=urllib.request.Request(RAW_URL+"?v="+str(now_ms()),headers={"User-Agent":"OnYVaCarnet/3.0","Cache-Control":"no-cache"})
                with urllib.request.urlopen(req,timeout=12) as response:
                    data=json.loads(response.read(16000000))
                if data.get("schemaVersion")!=1 or not data.get("cards"):raise ValueError("어휘 형식 오류")
                validate(data["cards"]);self.root.after(0,lambda:self.sync_result(data,manual))
            except Exception:self.root.after(0,lambda:self.sync_result(None,manual))
        threading.Thread(target=worker,daemon=True).start()
    def sync_result(self,data,manual):
        self.syncing=False
        if data is None:
            self.status.set("오프라인 · 저장된 "+str(len(self.s["cards"]))+"개 표현으로 학습할 수 있습니다.")
            if manual:messagebox.showinfo(TITLE,"새 어휘를 확인하지 못했습니다.\n저장된 단어로 계속 학습할 수 있습니다.",parent=self.root)
            return
        try:
            added=merge(self.s,data["cards"]);self.s["updated"]=max(self.s["updated"],data["updated"]);self.s["lastSync"]=now_ms();self.save();self.stats()
            if not self.current:self.next()
            if self.tabs.index("current")==1:self.render_library()
            self.status.set("어휘 기준 "+self.s["updated"]+" · "+str(len(self.s["cards"]))+"개 · "+("새 표현 "+str(added)+"개 추가" if added else "최신 상태"))
            if manual:messagebox.showinfo(TITLE,"새 표현 "+str(added)+"개를 추가했습니다." if added else "현재 어휘가 최신입니다.",parent=self.root)
        except Exception as e:self.status.set("업데이트를 적용하지 못했습니다. 기존 단어는 그대로입니다.");messagebox.showerror(TITLE,str(e),parent=self.root)
    def tick(self):
        if not self.current and self.tabs.index("current")==0:self.next()
        if not self.preview and now_ms()-self.s.get("lastSync",0)>15*60000 and not self.syncing:self.sync()
        self.root.after(30000,self.tick)
    def close(self):
        self.save();self.root.destroy()

def self_test(report):
    checks=[]
    def check(ok,name):
        if not ok:raise AssertionError(name)
        checks.append("PASS "+name)
    seed=embedded();check(len(seed["cards"])>=89,"89 embedded words without network")
    s=empty_state();merge(s,seed["cards"]);now=1793318400000;cid=s["cards"][0]["id"]
    check(len(queue(s,now))==10,"daily new limit");check(not queue(s,now,"ko"),"reverse initially locked")
    p=grade(None,"good",now);check(p["due"]==now+DAY,"one day after first success")
    p=grade(p,"good",now+DAY);s["progress"][cid+":fr"]=p
    check(unlocked(s,s["cards"][0]) and len(queue(s,now+DAY,"ko"))==1,"reverse unlock")
    check(grade(p,"again",now)["due"]==now+60000,"one minute relearning")
    check(grade(p,"hard",now)["due"]==now+600000,"ten minute relearning")
    count=len(s["cards"]);check(merge(s,seed["cards"])==0 and len(s["cards"])==count and s["progress"][cid+":fr"]==p,"merge preserves progress")
    check(day_key(1793285999000)!=day_key(1793286000000),"KST midnight")
    check(len(clean_state(json.loads(json.dumps(s)))["cards"])==count,"backup roundtrip")
    folder=Path(report).parent/"python-test-profile";store=Store(folder);store.state=s;store.save()
    check(Store(folder).state["progress"][cid+":fr"]["successes"]==2,"disk persistence")
    # Start actual native widgets, offline, with an isolated profile.
    root=tk.Tk();root.withdraw();app=App(root,folder,preview=True);root.update()
    check(len(app.s["cards"])==count and app.current is not None,"native window initializes offline")
    app.reveal();root.update();check(app.revealed and app.grade_buttons["good"].instate(["!disabled"]),"answer and grading UI")
    app.grade_click("good");root.update();check(len(app.s["activity"])==1,"native grading saves")
    app.query.set("격차");root.update();check(len(app.tree.get_children())==2,"Korean vocabulary search")
    root.destroy();checks.append("PASS "+str(len(checks))+" checks; "+str(count)+" words; "+seed["updated"])
    Path(report).write_text("\n".join(checks),encoding="utf-8")

def main():
    parser=argparse.ArgumentParser();parser.add_argument("--self-test");parser.add_argument("--preview");parser.add_argument("--install-only",action="store_true");parser.add_argument("--install",action="store_true");args=parser.parse_args()
    if args.self_test:self_test(args.self_test);return
    if args.install_only:install();return
    # One normal app window protects the same progress file from concurrent writers.
    if not args.preview:
        import ctypes
        global _app_mutex
        kernel=ctypes.WinDLL("kernel32",use_last_error=True)
        kernel.CreateMutexW.restype=ctypes.c_void_p
        _app_mutex=kernel.CreateMutexW(None,False,"Local\\OnYVaCarnetNative")
        if ctypes.get_last_error()==183:
            window=ctypes.windll.user32.FindWindowW(None,TITLE)
            if window:
                ctypes.windll.user32.ShowWindow(window,9)
                ctypes.windll.user32.SetForegroundWindow(window)
            return
    root=tk.Tk();app_home=HOME
    if args.install:
        root.withdraw()
        try:app_home=install().parent.parent
        except Exception as e:messagebox.showerror(TITLE,"설치하지 못했습니다.\n"+str(e),parent=root);root.destroy();return
        root.deiconify()
    try:App(root,args.preview or app_home/"Data",preview=bool(args.preview));root.mainloop()
    except Exception as e:messagebox.showerror(TITLE,"단어장을 열지 못했습니다.\n"+str(e),parent=root)

if __name__=="__main__":main()
