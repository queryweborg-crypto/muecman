import os
import discord
from discord.ext import commands
from discord import app_commands # Eğik çizgi komutları (Slash Commands) için
from google import genai # Google Gemini API için

## 🔒 1. Anahtarları Replit Secrets'ten Güvenli Okuma

# os.environ['ANAHTAR_ADI'] ile Replit Secrets (Ortam Değişkenleri)'den değerleri çeker
try:
    # Replit Secrets'te DISCORD_TOKEN ve GEMINI_API_KEY adında iki anahtarınız olmalı
    DISCORD_TOKEN = os.environ['DISCORD_TOKEN']
    GEMINI_API_KEY = os.environ['GEMINI_API_KEY']
except KeyError as e:
    # Anahtar bulunamazsa uyarı verir ve programı durdurur
    print(f"HATA: Replit Secrets'de {e} anahtarı bulunamadı. Lütfen kontrol edin.")
    print("Botu çalıştırmak için bu anahtarlar gereklidir.")
    exit()

## 🛠️ 2. Bot ve Gemini İstemcisi Kurulumu

# İhtiyacımız olan 'intents'leri tanımlıyoruz
# Slash komutları (app_commands) için varsayılan intentler yeterlidir.
intents = discord.Intents.default()
# Bot nesnesini oluşturuyoruz. Komut ön eki (command_prefix) slash komutlar için zorunlu değil.
bot = commands.Bot(command_prefix="!", intents=intents)

# Gemini İstemcisini Başlatma
ai_client = None
try:
    genai.configure(api_key=GEMINI_API_KEY)
    ai_client = genai.Client()
    print("🤖 Gemini API istemcisi başarıyla başlatıldı.")
except Exception as e:
    print(f"❌ Hata: Gemini API istemcisi başlatılamadı: {e}")

## 🚀 3. Olaylar ve Komutlar

@bot.event
async def on_ready():
    """Bot hazır olduğunda ve Discord'a bağlandığında çalışır."""
    print(f'✅ {bot.user} adıyla Discord\'a bağlandı!')
    
    # Eğik çizgi komutlarını (slash commands) Discord'a senkronize etme
    try:
        synced = await bot.tree.sync()
        print(f"🔄 Senkronize edilen {len(synced)} eğik çizgi komutu var.")
    except Exception as e:
        print(f"❌ Slash komut senkronizasyon hatası: {e}")


# --- Eğik Çizgi Komutu (/muec) ---

@bot.tree.command(name="muec", description="Yapay zekaya bir mesaj yaz ve cevap al.")
@app_commands.describe(
    mesaj="Yapay zekaya sormak istediğiniz soru veya mesaj."
)
async def muec_command(interaction: discord.Interaction, mesaj: str):
    """Kullanıcının yazdığı mesajı Gemini'a gönderir ve cevabı geri yollar."""
    
    # Kullanıcıya komutun işlendiğini bildirmek için defer (erteleme) yaparız.
    # Bu, AI'ın cevap vermesi zaman alsa bile Discord'un hata vermesini engeller.
    await interaction.response.defer() 
    
    # AI istemcisinin başarılı bir şekilde başlatılıp başlatılmadığını kontrol et
    if ai_client is None:
        await interaction.followup.send("❌ Hata: Yapay zeka servisi şu an kullanılamıyor. Lütfen API anahtarını kontrol edin.", ephemeral=True)
        return

    try:
        # Gemini modelini çağır
        response = ai_client.models.generate_content(
            model="gemini-2.5-flash", # Hızlı ve yetenekli model
            contents=mesaj
        )
        
        # Cevabı al
        cevap = response.text
        
        # Karakter sınırı kontrolü (Discord mesajları 2000 karakteri geçmemeli)
        if len(cevap) > 2000:
            cevap = cevap[:1997] + "..." # Mesajı kısalt
            
        # Kullanıcının komutuna cevap olarak mesajı gönder
        await interaction.followup.send(
            f"👤 **{interaction.user.display_name} Sordu:** *{mesaj}*\n"
            f"---"
            f"\n🤖 **Yapay Zeka Cevabı:**\n{cevap}"
        )

    except Exception as e:
        print(f"❌ Yapay zeka çağrısı hatası: {e}")
        await interaction.followup.send("Üzgünüm, yapay zekadan cevap alırken bir hata oluştu.", ephemeral=True)

## 🏃 4. Botu Çalıştırma

if __name__ == "__main__":
    # Botu Discord Token'ı ile çalıştır
    bot.run(DISCORD_TOKEN)
