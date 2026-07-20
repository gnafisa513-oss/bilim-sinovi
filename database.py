import sqlite3

DB_NAME = "workers.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS workers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            position TEXT NOT NULL,
            exam_date TEXT DEFAULT 'Muddati belgilanmagan'
        )
    ''')
    
    # Agar baza bo'sh bo'lsa xodimlarni yuklaymiz
    cursor.execute("SELECT COUNT(*) FROM workers")
    if cursor.fetchone()[0] == 0:
        initial_workers = [
            # Ma'muriyat
            ("Marajabov Abdukahxor", "Boshliq"), ("Matyo'kubov Elmirod", "Bosh muhandis"),
            ("Suyarkulov Shavkat", "IchTB muhandisi"), ("Do'lanov Otabek", "MXTX muhandisi"),
            ("Yusupov Asliddin", "DXShKB muhandisi"), ("Esajonova Dilnavoz", "MKCh noziri"),
            ("Turdimatov Baxrom", "Omborchi"), ("Mavlonov Alisher", "Qurilish bo'limi ustasi"),
            ("Dexkonov Ulugbek", "Haydovchi"), ("Sodiqov Xusniddin", "Haydovchi"),
            ("Rasulova Jamila", "Farrosh"), ("Tursunqulova Ziyoda", "Farrosh"),
            ("Ergashev Raximjon", "Qoravul"), ("Madvaliev Raximjon", "Qoravul"),
            ("Madaliev Kodirali", "Qoravul"),
            # TNB
            ("Djalolov Lazizibek", "Katta navbatchi"), ("Ko'shmatov Zafarjon", "Navbatchi"),
            ("Mamajonov Muzaffar", "Navbatchi"), ("Navruzmatov Muzaffar", "Navbatchi"),
            ("Normatov Odiljon", "Navbatchi"), ("Umarov Murodjon", "TNB el.monter"),
            ("Kulmiddinov Umidjon", "TNB el.monter"), ("Xalilov Azizbek", "TNB el.monter"),
            ("Sultonaliev Umidjon", "TNB el.monter"), ("Saxroev Baxodir", "TNB el.monter"),
            ("Tuxtasinov Doston", "TNB haydovchi"), ("Isroilov Ramizbek", "TNB haydovchi"),
            ("Shermatov Xursandbek", "TNB haydovchi"), ("Ma'mirxonov Farxod", "TNB haydovchi"),
            ("Sotvoldiev Shamsiddin", "TNB haydovchi"),
            # 1-bo'lim
            ("Muxiddinov Asliddin", "1-bo'lim ustasi"), ("Umarov Furkat", "Elektromonter"),
            ("Xusanov Azizbek", "Elektromonter"), ("Jamolov Murodil", "Elektromonter"),
            ("Pozilov Maxmudjon", "Elektromonter"),
            # 2-bo'lim
            ("Axmedov Toxirjon", "2-bo'lim ustasi"), ("Solijonov Sarvar", "Elektromonter"),
            ("Tursunaliev Muxriddin", "Elektromonter"), ("Xamrokulova Mayramxon", "Elektromonter"),
            ("Boltaboev Zafarjon", "Elektromonter"), ("Valiev Avazbek", "Haydovchi"),
            # 3-bo'lim
            ("Xojiev Abduvaxob", "3-bo'lim ustasi"), ("Toybolaev Raxim", "Elektromonter"),
            ("Allonov Abdumalik", "Elektromonter"), ("Ganiev Muxammadyosuf", "Elektromonter"),
            ("Axmedov Maxammad", "Elektromonter"), ("Ibragimov Xusanboy", "Elektromonter"),
            ("Yadgorov Azizbek", "Haydovchi"),
            # 4-bo'lim
            ("Xolmatov Saidabrorxon", "4-bo'lim ustasi"), ("Ibroximov Bunyod", "Elektromonter"),
            ("Abdullaeva Guljaxon", "Elektromonter"), ("Tursunaliev Lazizbek", "Elektromonter"),
            ("Olimov Akramjon", "Elektromonter"),
            # 5-bo'lim
            ("Mirzakarimov Ibroxim", "5-bo'lim ustasi"), ("Nasibullaev Jaloldin", "Elektromonter"),
            ("Ganieva Nafisa", "Elektromonter"), ("Xaitov Ilxomjon", "Haydovchi"),
            ("Maxkamov Zafarjon", "Elektromonter"),
            # Kup kavatli 0.4kv
            ("Ibragimov Nodirbek", "Usta"), ("Jo'raeva Munavvar", "Elektromonter"),
            ("Tojiboev Dilshod", "Elektromonter"), ("Abdulazizov Rasulbek", "Elektromonter"),
            ("Matyo'kubov Sherzod", "Elektromonter"),
            # ASKUY bo'limi
            ("Olimjonov Abror", "IKB o'rinbosari"), ("Xolboev Abdurashid", "ASKUY guruhi boshligi"),
            ("Mukimov Jaxongir", "OPK"), ("Atabekova Nargiza", "ASKUY operatori"),
            ("Navro'zmatov Izzat", "ASKUY muhandisi"), ("Xamrokulova Nilufar", "ASKUY operatori"),
            ("Muxiddinov Zuxriddin", "zamen scet"), ("Axmedov Ilxomjon", "zamen scet"),
            ("Mamajonov Bexruz", "ASKUY muhandisi")
        ]
        cursor.executemany("INSERT INTO workers (name, position) VALUES (?, ?)", initial_workers)
        conn.commit()
    conn.close()

init_db()