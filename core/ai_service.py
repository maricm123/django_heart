import openai
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

def generate_session_summary(training_session, coach) -> str:
    if not settings.OPENAI_API_KEY:
        logger.warning("OpenAI API key not configured")
        return "Great session today! Keep up the excellent work!"
    
    try:
        client = openai.OpenAI(api_key=settings.OPENAI_API_KEY)
        
        # Pripremi prompt
        metrics = training_session.summary_metrics or {}
        summary = metrics.get('summary', {})
        
        prompt = f"""
            Napiši personalizovanu poruku za klijenta nakon završene trening sesije.

            Cilj:
            - Poruka treba da bude podržavajuća, stručna, motivišuća i prirodna.
            - Piši isključivo na osnovu dostupnih metrika.
            - Nemoj izmišljati napredak, tehniku izvođenja, zdravstveno stanje ili rezultate koji nisu direktno vidljivi iz podataka.

            Obavezna pravila:
            - Piši na srpskom jeziku.
            - Obraćaj se direktno klijentu.
            - Napiši 8 do 10 rečenica.
            - Poruka treba da bude nešto duža, toplija i sadržajnija, ali i dalje pogodna za prikaz u aplikaciji.
            - Bez emoji-ja.
            - Bez generičkih fraza poput "sjajno", "brutalno", "pokidao/la si".
            - Ako neka metrika ne postoji, nemoj je pominjati.

            Kako da strukturiraš poruku:
            1. Prva rečenica neka bude kratak osvrt na sesiju kao celinu.
            2. Druga i treća rečenica neka prokomentarišu trajanje, kalorije i/ili puls, ali samo ako ti podaci postoje.
            3. Jedna rečenica neka da praktičan savet za oporavak, hidrataciju, ishranu ili odmor.
            4. Poslednja rečenica neka bude motivaciona i prirodna, bez preterivanja.

            Pravila za interpretaciju:
            - Ako trening traje ispod 30 minuta, naglasi da je sesija bila kraća, ali da kontinuitet i kraći kvalitetni treninzi imaju vrednost.
            - Ako trening traje 30 minuta ili više, naglasi dobar rad i izdržljivost.
            - Ako su kalorije više, kratko pomeni hidrataciju i kvalitetan obrok nakon treninga.
            - Ako je maksimalni puls visok, kratko pomeni važnost oporavka i sna, bez medicinskih tvrdnji.
            - Ako su puls i kalorije umereni, opiši sesiju kao stabilan i koristan trening.

            Podaci o sesiji:
            - Naziv sesije: {training_session.title}
            - Trajanje: {format_duration(training_session.duration)}
            - Kalorije: {summary.get('calories', 0):.0f}
            - Prosečan puls: {summary.get('avg_hr', 'N/A')} bpm
            - Maksimalni puls: {summary.get('max_hr', 'N/A')} bpm
            - Coach: {coach.user.name}

            Vrati samo finalnu poruku, bez naslova, bez uvoda i bez navodnika.
            """
        
        response = client.chat.completions.create(
            model=settings.OPENAI_MODEL,
            messages=[
                {
                    "role": "system",
                    "content": "Ti si AI coach asistent koji daje personalizovane poruke o treninzima. Budi realan i motivacijski."

                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=settings.OPENAI_TEMPERATURE,
            max_tokens=100,
        )

        return response.choices[0].message.content.strip()
        
    except Exception as e:
        logger.error(f"OpenAI API error: {str(e)}")
        return "Excellent session! Your effort is building your strength."


def format_duration(seconds):
    """Format seconds to HH:MM:SS"""
    if not seconds:
        return "N/A"
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    secs = seconds % 60
    return f"{hours:02d}:{minutes:02d}:{secs:02d}"
