import discord
import random
import json
import os
import asyncio

# AYARLAR
TOKEN = os.getenv("TOKEN")  # <-- Eskiden burası düz yazılmış token idi
# if message.channel.id != SAYI_KANAL_ID:
#     return
SAYI_DOSYA = "sayi_veri.json"

def veri_yukle():
    if os.path.exists(SAYI_DOSYA):
        with open(SAYI_DOSYA, 'r') as f:
            return json.load(f)
    return {
        "son_sayi": 0,
        "son_kullanici": 0,
        "aktif_blok": 1,
        "boomlar": []
    }

def veri_kaydet(data):
    with open(SAYI_DOSYA, 'w') as f:
        json.dump(data, f)

def yeni_blok_olustur(blok_no):
    baslangic = (blok_no - 1) * 30 + 1
    bitis = blok_no * 30
    boom1 = random.randint(baslangic, bitis)
    boom2 = random.randint(baslangic, bitis)
    while boom2 == boom1:
        boom2 = random.randint(baslangic, bitis)
    return sorted([boom1, boom2])

intents = discord.Intents.default()
intents.message_content = True

class SayiBot(discord.Client):
    def __init__(self):
        super().__init__(intents=intents)
    
    async def on_ready(self):
        print(f"🤖 {self.user.name} hazır!")
        
        veri = veri_yukle()
        if veri["son_sayi"] == 0:
            veri["boomlar"] = yeni_blok_olustur(1)
            veri_kaydet(veri)
            
            kanal = self.get_channel(SAYI_KANAL_ID)
            if kanal:
                embed = discord.Embed(
                    title="🎯 SAYI SAYMACA BAŞLADI!",
                    description="Sırayla sayı yaz! Her 30 sayıda 2 BOOM var! 💥",
                    color=0x00ff00
                )
                embed.add_field(
                    name="📝 Kurallar",
                    value="• Sırayla sayı yaz (1, 2, 3...)\n• Aynı kişi arka arkaya yazamaz\n• Yanlış sayı silinir\n• Her 30 sayıda 2 BOOM!",
                    inline=False
                )
                await kanal.send(embed=embed)
                print(f"💥 Bu bloktaki BOOM'lar: {veri['boomlar']}")
    
    async def on_message(self, message):
        if message.author.bot:
            return
        
        if message.channel.id != SAYI_KANAL_ID:
            return
        
        veri = veri_yukle()
        
        try:
            sayi = int(message.content.strip())
            beklenen = veri["son_sayi"] + 1
            
            if message.author.id == veri["son_kullanici"]:
                await message.delete()
                uyari = await message.channel.send(
                    f"⏳ {message.author.mention} **Sıranı bekle!**"
                )
                await asyncio.sleep(3)
                await uyari.delete()
                return
            
            if sayi != beklenen:
                await message.delete()
                return
            
            if sayi > 10000:
                await message.channel.send("🎉 **10000 TAMAMLANDI!** Oyun bitti!")
                veri = {"son_sayi": 0, "son_kullanici": 0, "aktif_blok": 1, "boomlar": yeni_blok_olustur(1)}
                veri_kaydet(veri)
                return
            
            await message.add_reaction("✅")
            
            mevcut_blok = (sayi - 1) // 30 + 1
            if mevcut_blok != veri["aktif_blok"]:
                veri["aktif_blok"] = mevcut_blok
                veri["boomlar"] = yeni_blok_olustur(mevcut_blok)
                veri_kaydet(veri)
                
                baslangic = (mevcut_blok - 1) * 30 + 1
                bitis = mevcut_blok * 30
                embed = discord.Embed(
                    title=f"🎯 YENİ BLOK: {baslangic}-{bitis}",
                    description=f"Yeni 2 BOOM gizlendi! 💥💥",
                    color=0x3498db
                )
                await message.channel.send(embed=embed)
                print(f"💥 Yeni blok {baslangic}-{bitis} BOOM'lar: {veri['boomlar']}")
            
            if sayi in veri["boomlar"]:
                await asyncio.sleep(0.5)
                
                boom_embed = discord.Embed(
                    title="💥 BOOM!",
                    description=f"{message.author.mention} **{sayi}**'de patladı!",
                    color=0xff0000
                )
                await message.channel.send(embed=boom_embed)
                
                veri["boomlar"].remove(sayi)
            
            veri["son_sayi"] = sayi
            veri["son_kullanici"] = message.author.id
            veri_kaydet(veri)
            
        except ValueError:
            await message.delete()

bot = SayiBot()

if TOKEN is None:
    print("⚠️ TOKEN environment variable olarak ayarlanmalı!")
else:
    bot.run(TOKEN)
