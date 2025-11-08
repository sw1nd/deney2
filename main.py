# main.py

# --- EXE (--noconsole) kapanışında logging'in patlamasını engelle ---
import sys, io, os, csv, glob, datetime
from PIL import Image

class _DevNull(io.TextIOBase):
    def write(self, s): return len(s or "")
    def flush(self): pass

# PyInstaller'da stdout/stderr None olabilir -> yazılabilir hedef ver
if sys.stdout is None: sys.stdout = _DevNull()
if sys.stderr is None: sys.stderr = _DevNull()
# --------------------------------------------------------------------

from psychopy import visual, core, event, gui, logging

# Konsol loglarını kapat, stream'i garanti et
try:
    logging.console.setLevel(logging.CRITICAL + 1)
    if getattr(logging.console, "stream", None) is None:
        logging.console.stream = _DevNull()
except Exception:
    pass


def resource_path(*parts):
    # PyInstaller onefile için gömülü kaynak yolu
    if hasattr(sys, '_MEIPASS'):
        base = sys._MEIPASS
    else:
        base = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base, *parts)


def get_data_dir():
    """
    Windows/macOS'ta güvenli veri klasörü. Öncelik: Documents/Belgeler.
    OneDrive yönlendirmelerini de dener.
    """
    home = os.path.expanduser("~")
    candidates = []

    if sys.platform.startswith("win"):
        up = os.environ.get("USERPROFILE", home)
        od = os.environ.get("OneDrive") or os.environ.get("OneDriveConsumer")
        candidates = [
            os.path.join(up, "Documents"),
            os.path.join(up, "Belgeler"),
        ]
        if od:
            candidates.append(os.path.join(od, "Documents"))
            candidates.append(os.path.join(od, "Belgeler"))
    else:
        candidates = [os.path.join(home, "Documents")]

    for base in candidates:
        try:
            path = os.path.join(base, "DeneyVerileri")
            os.makedirs(path, exist_ok=True)
            return path
        except Exception:
            continue

    # Son çare: ev klasörü
    path = os.path.join(home, "DeneyVerileri")
    os.makedirs(path, exist_ok=True)
    return path


def safe_exit(win=None, code=0):
    """core.quit yerine güvenli çıkış; logging flush yazma hatalarını engeller."""
    try:
        if hasattr(logging, "console"):
            if getattr(logging.console, "stream", None) is None:
                logging.console.stream = _DevNull()
            logging.console.setLevel(logging.CRITICAL + 1)
            try:
                logging.flush()
            except Exception:
                pass
    except Exception:
        pass
    if win is not None:
        try:
            win.close()
        except Exception:
            pass
    sys.exit(code)


# ------------------ Ayarlar ------------------
FULLSCREEN = True
BG_COLOR = 'black'
TEXT_COLOR = 'white'
FONT_NAME = 'Arial'

PHOTO_MAX_SEC = 10.0
SKIP_KEY = 's'            # fotoğrafı geçmek için tuş
EXIT_KEY = 'escape'       # acil çıkış

LIKERT_KEYS = ['1','2','3','4','5','6','7']  # 7'li Likert
FRIEND_KEYS = ['e','h']   # e=Evet, h=Hayır

STIM_ROOT = resource_path('stimuli')
DATA_DIR = get_data_dir()

# Sorular (10 adet)
LIKERT_QUESTIONS = [
    "Bu kişi dışa dönük, sosyal, konuşkan biridir.",
    "Bu kişi eleştirel, tartışmacı biridir.",
    "Bu kişi güvenilir, öz-disiplinli biridir.",
    "Bu kişi endişeli, kolay üzülen biridir.",
    "Bu kişi yaratıcı, orijinal, yeni fikirlere açık biridir.",
    "Bu kişi başkalarına karşı ilgili ve yardımsever olmayan biridir.",
    "Bu kişi tembel biridir.",
    "Bu kişi yeni deneyimlere açık olmayan, geleneksel biridir.",
    "Bu kişi başkalarıyla kolayca anlaşan, nazik biridir.",
    "Bu kişi düzenli, titiz biridir."
]

LIKERT_SCALE_HINT = "1 = Hiç Katılmıyorum  …  7 = Tamamen Katılıyorum"
FRIENDSHIP_QUESTION = "Bu kişiyle arkadaş olmak ister misiniz? (Evet/Hayır)"

CONSENT_TEXT = """Sayın Katılımcı,

Bu araştırma Atılım Üniversitesi Klinik Psikoloji Yüksek Lisans Programı kapsamında Doç. Dr. Neşe Alkan danışmanlığında Mine Ayasulu tarafından yürütülmektedir. Araştırmanın amacı insanların Instagram'da paylaştığı görsellerin Beş Faktör Kişilik Özellikleri ile ne ölçüde örtüştüğünü ölçmeyi amaçlamaktadır. Bu ölçümü yaparken psikologlar ve psikolog olmayanlar, Instagram gönderilerini paylaşmayı kabul eden katılımcıları beş faktör kişilik analizine göre değerlendirecektir.

Araştırmaya katılımınız halinde, Instagram görsellerine dayanarak kişilik özelliklerini değerlendirmeniz istenecek ve her bir kişi için Ten Item Personality Inventory (TIPI) maddelerini yanıtlamanız beklenecektir. TIPI, bir bireyin kişilik özelliklerini genel hatlarıyla değerlendirmeye yönelik 10 maddelik kısa bir testtir. Her bir Instagram görseli ekranda 10 saniye boyunca gösterilecektir. Bir kişiye ait üç görseli inceledikten sonra, o kişiye dair izleniminize dayanarak Ten Item Personality Inventory (TIPI) testini doldurmanız beklenecektir. Daha sonra ekrana bu kişiyle arkadaş olmak ister misin? Sorusu gelecektir. Yaptığınız değerlendirmeler, yalnızca araştırmanın amacı doğrultusunda kullanılacak ve herhangi bir kişisel bilgiyi içermeyecektir. Çalışmaya katılımınız tamamen gönüllülük esasına dayanmaktadır. Çalışmanın süresi yaklaşık on dakika olacaktır. Çalışmaya katılmayı reddedebilir veya katıldıktan sonra istediğiniz aşamada, gerekçe göstermeksizin ayrılabilirsiniz. Çalışmadan ayrılmanız durumunda sizden toplanan veriler imha edilecektir.

Test, özel hayatınıza müdahale edecek ya da psikolojik rahatsızlık yaratacak herhangi bir içerik barındırmaz. Ancak herhangi bir nedenden dolayı testi uygulamak istemezseniz, araştırmadan neden belirtmeden ayrılmakta özgürsünüz. Çalışmaya katılımınız için şimdiden teşekkür ederim. Çalışma hakkında daha fazla bilgi almak isterseniz araştırmayı yürüten Mine Ayasulu ile (psk.mineayasulu@gmail.com) iletişime geçebilirsiniz.
"""

LIKERT_INSTRUCTION = "Lütfen bir yanıt seçin (1–7 tuşları veya butonlara tıklayın). Boş bırakma yok."
PHOTO_HINT = f"Fotoğraf en fazla {int(PHOTO_MAX_SEC)} sn gösterilecek. Geçmek için [{SKIP_KEY.upper()}] tuşuna basın veya fotoğrafa tıklayın"

LIKERT_LABELS = {
    '1': 'Hiç Katılmıyorum',
    '2': 'Katılmıyorum',
    '3': 'Biraz Katılmıyorum',
    '4': 'Ne Katılıyorum Ne Katılmıyorum',
    '5': 'Biraz Katılıyorum',
    '6': 'Katılıyorum',
    '7': 'Tamamen Katılıyorum'
}

# ------------------ Yardımcılar ------------------
def ensure_dir(path):
    if not os.path.exists(path):
        os.makedirs(path)

def list_sets(stim_root):
    sets = sorted([d for d in glob.glob(os.path.join(stim_root, 'set*')) if os.path.isdir(d)])
    return sets

def list_images(set_folder):
    exts = ('.jpg', '.jpeg', '.png', '.bmp')
    imgs = sorted([p for p in glob.glob(os.path.join(set_folder, '*')) if p.lower().endswith(exts)])
    return imgs[:3]  # İlk 3 görsel

def get_image_size(img_path):
    """Görüntünün orijinal boyutlarını döndürür"""
    try:
        with Image.open(img_path) as img:
            return img.size  # (width, height)
    except Exception:
        return None

def calculate_image_size(img_path, max_width=1.6, max_height=0.9):
    """Görüntüyü aspect ratio'yu koruyarak ekrana sığdırır"""
    img_size = get_image_size(img_path)
    if img_size is None:
        return (max_width, max_height)  # Varsayılan boyut
    
    img_width, img_height = img_size
    aspect_ratio = img_width / img_height
    
    # Ekran aspect ratio'su (height units kullanıyoruz)
    max_aspect = max_width / max_height
    
    if aspect_ratio > max_aspect:
        # Görüntü daha geniş, genişliğe göre ölçekle
        width = max_width
        height = max_width / aspect_ratio
    else:
        # Görüntü daha yüksek, yüksekliğe göre ölçekle
        height = max_height
        width = max_height * aspect_ratio
    
    return (width, height)

def draw_centered_text(win, text, height=0.06, pos=(0,0)):
    stim = visual.TextStim(
        win, text=text, color=TEXT_COLOR, font=FONT_NAME,
        height=height, wrapWidth=1.6, pos=pos
    )
    stim.draw()

def wait_key(win, key_list):
    while True:
        keys = event.waitKeys(keyList=key_list + [EXIT_KEY], timeStamped=True)
        for k, t in keys:
            if k == EXIT_KEY:
                safe_exit(win)
            if k in key_list:
                return k, t

def create_likert_buttons(win):
    """Likert ölçeği için 1-7 butonları oluşturur"""
    buttons = []
    button_width = 0.14
    button_height = 0.08
    spacing = 0.03
    total_width = 7 * button_width + 6 * spacing
    start_x = -total_width / 2 + button_width / 2
    
    for i, key in enumerate(LIKERT_KEYS):
        x_pos = start_x + i * (button_width + spacing)
        rect = visual.Rect(
            win, width=button_width, height=button_height,
            pos=(x_pos, -0.25), fillColor='gray', lineColor='white',
            lineWidth=2, units='height'
        )
        label = visual.TextStim(
            win, text=key, color=TEXT_COLOR, font=FONT_NAME,
            height=0.04, pos=(x_pos, -0.25), units='height'
        )
        # Açıklama metnini kısalt - çok uzun metinleri kısalt
        desc_text = LIKERT_LABELS[key]
        # Uzun metinleri iki satıra böl
        if len(desc_text) > 18:
            words = desc_text.split()
            mid = len(words) // 2
            if mid > 0:
                desc_text = ' '.join(words[:mid]) + '\n' + ' '.join(words[mid:])
            else:
                # Tek kelime ise ortadan böl
                mid_char = len(desc_text) // 2
                desc_text = desc_text[:mid_char] + '\n' + desc_text[mid_char:]
        
        desc = visual.TextStim(
            win, text=desc_text, color=TEXT_COLOR, font=FONT_NAME,
            height=0.02, pos=(x_pos, -0.36), units='height',
            wrapWidth=button_width * 0.85, alignText='center'
        )
        buttons.append({
            'key': key,
            'rect': rect,
            'label': label,
            'desc': desc,
            'x': x_pos,
            'width': button_width,
            'height': button_height
        })
    return buttons

def create_yes_no_buttons(win, evet_text='E: Evet', hayir_text='H: Hayır', y_pos=-0.25):
    """Evet/Hayır butonları oluşturur (onam ve arkadaşlık için)"""
    buttons = []
    # Metin uzunluğuna göre buton genişliğini ayarla
    max_text_len = max(len(evet_text), len(hayir_text))
    if max_text_len > 12:  # Uzun metinler için daha geniş buton
        button_width = 0.35
        button_height = 0.12
        text_height = 0.035
    else:
        button_width = 0.25
        button_height = 0.12
        text_height = 0.04
    spacing = 0.1
    
    # Evet butonu
    evet_rect = visual.Rect(
        win, width=button_width, height=button_height,
        pos=(-button_width/2 - spacing/2, y_pos), fillColor='gray',
        lineColor='white', lineWidth=2, units='height'
    )
    evet_label = visual.TextStim(
        win, text=evet_text, color=TEXT_COLOR, font=FONT_NAME,
        height=text_height, pos=(-button_width/2 - spacing/2, y_pos), 
        units='height', wrapWidth=button_width * 0.9, alignText='center'
    )
    buttons.append({
        'key': 'e',
        'rect': evet_rect,
        'label': evet_label,
        'x': -button_width/2 - spacing/2,
        'y': y_pos,
        'width': button_width,
        'height': button_height
    })
    
    # Hayır butonu
    hayir_rect = visual.Rect(
        win, width=button_width, height=button_height,
        pos=(button_width/2 + spacing/2, y_pos), fillColor='gray',
        lineColor='white', lineWidth=2, units='height'
    )
    hayir_label = visual.TextStim(
        win, text=hayir_text, color=TEXT_COLOR, font=FONT_NAME,
        height=text_height, pos=(button_width/2 + spacing/2, y_pos), 
        units='height', wrapWidth=button_width * 0.9, alignText='center'
    )
    buttons.append({
        'key': 'h',
        'rect': hayir_rect,
        'label': hayir_label,
        'x': button_width/2 + spacing/2,
        'y': y_pos,
        'width': button_width,
        'height': button_height
    })
    
    return buttons

def create_friend_buttons(win):
    """Arkadaşlık sorusu için Evet/Hayır butonları oluşturur"""
    return create_yes_no_buttons(win, 'E: Evet', 'H: Hayır', -0.25)

def wait_key_or_click(win, key_list, buttons, draw_func=None):
    """Hem klavye hem de buton tıklamalarını bekler
    
    Args:
        win: PsychoPy window
        key_list: Geçerli klavye tuşları listesi
        buttons: Buton listesi
        draw_func: Opsiyonel, ekranı çizmek için fonksiyon (soru metni vs. için)
    """
    mouse = event.Mouse(win=win)
    timer = core.Clock()
    start_time = timer.getTime()
    
    # İlk ekranı çiz
    if draw_func:
        draw_func()
    for btn in buttons:
        btn['rect'].draw()
        btn['label'].draw()
        if 'desc' in btn:
            btn['desc'].draw()
    win.flip()
    
    while True:
        # Klavye kontrolü
        keys = event.getKeys(keyList=key_list + [EXIT_KEY], timeStamped=True)
        for k, t in keys:
            if k == EXIT_KEY:
                safe_exit(win)
            if k in key_list:
                return k, t
        
        # Mouse kontrolü - tıklama olayını kontrol et
        mouse_clicked = mouse.getPressed()[0]
        if mouse_clicked:
            # Tıklama bırakılana kadar bekle (basılı tutma durumunu önlemek için)
            while mouse.getPressed()[0]:
                core.wait(0.01)
            mouse_pos = mouse.getPos()
            for btn in buttons:
                btn_x = btn['x']
                btn_y = btn.get('y', -0.25)  # Varsayılan y pozisyonu
                btn_width = btn['width']
                btn_height = btn['height']
                # Buton sınırlarını kontrol et (height units kullanıyoruz)
                if (btn_x - btn_width/2 <= mouse_pos[0] <= btn_x + btn_width/2 and
                    btn_y - btn_height/2 <= mouse_pos[1] <= btn_y + btn_height/2):
                    rt = timer.getTime() - start_time
                    return btn['key'], rt
        
        core.wait(0.01)  # CPU kullanımını azalt


# ------------------ Başlat ------------------
def main():
    # --- DEMOGRAFİK BİLGİLER (ZORUNLU) ---  # İngilizce satırı gizler
    # --- DEMOGRAFİK BİLGİLER (ZORUNLU; etiketlerde * var, İngilizce satır gizlenir) ---
    while True:
        dlg = gui.Dlg(title="Katılımcı Bilgileri")  # İngilizce 'required' uyarısını kaldır

        # Etiketlerde * gösterimi
        dlg.addField("Ad - Soyad :")
        dlg.addField("Yaş :")
        dlg.addField("Eğitim durumu :")
        dlg.addField("Meslek :")
        dlg.addField("E-posta :")

        ok = dlg.show()
        if not dlg.OK:
            safe_exit(None)  # İptal → çık

        name_surname = (ok[0] or "").strip()
        age         = (ok[1] or "").strip()
        education   = (ok[2] or "").strip()
        profession  = (ok[3] or "").strip()
        email       = (ok[4] or "").strip()

        # Zorunlu alan kontrolü
        missing = [lbl for lbl, val in [
            ("Ad - Soyad", name_surname),
            ("Yaş", age),
            ("Eğitim durumu", education),
            ("Meslek", profession),
            ("E-posta", email),
        ] if not val]

        # (Opsiyonel) çok basit e-posta biçim kontrolü
        if email and ("@" not in email or "." not in email.split("@")[-1]):
            missing.append("E-posta (geçerli biçim)")

        if not missing:
            participant = name_surname  # artık boş olamaz
            break

        err = gui.Dlg(title="Eksik/Geçersiz Bilgi")
        err.addText("Tüm alanlar ZORUNLUDUR. Lütfen düzeltin:\n- " + "\n- ".join(missing))
        err.show()

    timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
    ensure_dir(DATA_DIR)

    # Dosya yolları
    base = f"{participant}_{timestamp}"
    results_csv = os.path.join(DATA_DIR, f"{base}_sonuclar.csv")

    # CSV'yi oluştur ve başlığı bir kez yaz
    with open(results_csv, "w", newline="", encoding="utf-8-sig") as f:
        w = csv.writer(f)
        w.writerow([
            "participant","timestamp","phase",
            "set_index","item_index","item_text",
            "response_key","response_label","rt_sec"
        ])

    # Pencere
    win = visual.Window(fullscr=FULLSCREEN, color=BG_COLOR, units='height')
    win.mouseVisible = True  # Butonlar için mouse görünür olmalı

    # ------------------ Onam ------------------
    event.clearEvents()
    consent_buttons = create_yes_no_buttons(win, 'E: Onaylıyorum', 'H: Onaylamıyorum', -0.35)
    def draw_consent_screen():
        draw_centered_text(win, CONSENT_TEXT, height=0.025, pos=(0, 0.1))
    key, t = wait_key_or_click(win, ['e','h'], consent_buttons, draw_consent_screen)
    consent_given = (key == 'e')

    # Onam kaydı
    with open(results_csv, 'a', newline='', encoding='utf-8-sig') as f:
        w = csv.writer(f)
        w.writerow([participant, timestamp, "consent",
                    "", "", "Consent",
                    key, ("onay" if consent_given else "ret"), f"{t:.4f}"])

    if not consent_given:
        event.clearEvents()
        draw_centered_text(win, "Onay verilmedi. Deney sonlandırılıyor.", height=0.05)
        win.flip()
        core.wait(2.0)
        safe_exit(win)

    # --- Onam VERİLDİYSE demografik cevapları kaydet ---
    demographics = [
        ("Ad - Soyad", name_surname),
        ("Yaş", age),
        ("Eğitim durumu", education),
        ("Meslek", profession),
        ("E-posta", email),
    ]
    with open(results_csv, 'a', newline='', encoding='utf-8-sig') as f:
        w = csv.writer(f)
        for label, value in demographics:
            w.writerow([participant, timestamp, "demographics",
                        "", "", label, value, value, ""])

    # ------------------ Setleri hazırla ------------------
    sets = list_sets(STIM_ROOT)
    if len(sets) < 10:
        print(f"[Uyarı] Bulunan set sayısı: {len(sets)} (beklenen: 10)")

    # ------------------ Deney Döngüsü ------------------
    total_sets = min(10, len(sets))  # 10 set
    timer = core.Clock()
    mouse = event.Mouse(win=win)  # Mouse'u bir kez oluştur

    for si in range(total_sets):
        set_folder = sets[si]
        images = list_images(set_folder)
        if len(images) != 3:
            print(f"[Uyarı] {set_folder} içinde 3 görsel bulunamadı. Bulunan: {len(images)}")

        # --- 3 Fotoğraf (max 10 sn, SKIP ile geç veya tıklayarak geç) ---
        for img_path in images:
            # Görüntü boyutunu aspect ratio'yu koruyarak hesapla
            img_size = calculate_image_size(img_path, max_width=1.6, max_height=0.9)
            pic = visual.ImageStim(win, image=img_path, size=img_size, units='height')
            hint = visual.TextStim(win, text=PHOTO_HINT, color=TEXT_COLOR, font=FONT_NAME, height=0.03, pos=(0,-0.45))
            event.clearEvents()
            timer.reset()
            while timer.getTime() < PHOTO_MAX_SEC:
                pic.draw()
                hint.draw()
                win.flip()
                
                # Klavye kontrolü
                keys = event.getKeys(keyList=[SKIP_KEY, EXIT_KEY])
                if EXIT_KEY in keys:
                    safe_exit(win)
                if SKIP_KEY in keys:
                    break
                
                # Mouse tıklama kontrolü - fotoğrafa tıklanınca geç
                if mouse.getPressed()[0]:  # Sol tık
                    # Tıklama bırakılana kadar bekle
                    while mouse.getPressed()[0]:
                        core.wait(0.01)
                    mouse_pos = mouse.getPos()
                    # Fotoğrafın sınırlarını kontrol et (merkez 0,0)
                    img_width, img_height = img_size
                    if (-img_width/2 <= mouse_pos[0] <= img_width/2 and
                        -img_height/2 <= mouse_pos[1] <= img_height/2):
                        break

        # --- 10 Likert soru (boş bırakılamaz) ---
        likert_buttons = create_likert_buttons(win)
        for qi, qtext in enumerate(LIKERT_QUESTIONS, start=1):
            event.clearEvents()
            # Çizim fonksiyonu
            def draw_likert_screen():
                draw_centered_text(win, f"Soru {qi}/10\n\n{qtext}", height=0.05, pos=(0, 0.1))
                draw_centered_text(win, LIKERT_INSTRUCTION, height=0.035, pos=(0, -0.05))
                draw_centered_text(win, LIKERT_SCALE_HINT, height=0.03, pos=(0, -0.12))
            
            resp_key, rt = wait_key_or_click(win, LIKERT_KEYS, likert_buttons, draw_likert_screen)

            with open(results_csv, 'a', newline='', encoding='utf-8-sig') as f:
                w = csv.writer(f)
                w.writerow([
                    participant, timestamp, "likert",
                    si+1, qi, qtext,
                    resp_key, LIKERT_LABELS.get(resp_key, resp_key), f"{rt:.4f}"
                ])

        # --- Arkadaşlık Sorusu (E/H) ---
        event.clearEvents()
        friend_buttons = create_friend_buttons(win)
        # Çizim fonksiyonu
        def draw_friend_screen():
            draw_centered_text(win, FRIENDSHIP_QUESTION, height=0.05, pos=(0, 0.05))
           
        
        f_key, f_rt = wait_key_or_click(win, FRIEND_KEYS, friend_buttons, draw_friend_screen)
        friend_resp = "Evet" if f_key == 'e' else "Hayır"

        with open(results_csv, 'a', newline='', encoding='utf-8-sig') as f:
            w = csv.writer(f)
            w.writerow([
                participant, timestamp, "friendship",
                si+1, "", "Arkadaşlık",
                f_key, friend_resp, f"{f_rt:.4f}"
            ])

    # ------------------ Teşekkür ------------------
    event.clearEvents()
    draw_centered_text(win, "Teşekkür ederiz.\n\nDeney tamamlandı.", height=0.06)
    win.flip()
    core.wait(2.5)

    # Güvenli kapanış
    safe_exit(win, 0)


if __name__ == "__main__":
    main()