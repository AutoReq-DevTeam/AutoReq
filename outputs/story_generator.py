"""
outputs/story_generator.py — User Story Üretim Modülü
Sorumlu: Halise İncir
"""

import json
from typing import List, Dict
from core.models import AnalysisReport
from modules.llm_client import LLMClient, LLMClientError

class StoryGenerator:
    """Gereksinimlerden hem Türkçe hem İngilizce User Stories üretir."""

    def __init__(self, llm_client: LLMClient | None = None) -> None:
        self._llm = llm_client or LLMClient()

    def _build_prompt(self, text: str, language: str) -> str:
        # Kabul kriterindeki "As a [Actor], I want [Action] so that [Value]" formatını buraya çiviledik.
        target_lang = "Turkish" if language == "tr" else "English"
        
        return f"""
Convert the following requirement into a professional Agile User Story.
The output MUST follow this exact template: "As a [Actor], I want [Action], so that [Value]".

Requirement:
{text}

Output MUST be a valid JSON with these keys:
{{
  "role": "The actor/role",
  "goal": "The action/want",
  "benefit": "The value/benefit",
  "full_story": "The complete 'As a... I want... so that...' string in {target_lang}",
  "acceptance_criteria": ["criteria 1", "criteria 2"]
}}

Language of the content: {target_lang}
"""

    def generate(self, report: AnalysisReport, language: str = "tr") -> List[Dict]:
        """
        Gereksinimleri ve GAP'leri User Story listesine dönüştürür.
        """
        stories: List[Dict] = []
        
        # İşlenecek tüm maddeleri birleştiriyoruz
        items_to_process = []
        
        # --- HATA BURADAYDI, DÜZELTİLDİ ---
        # report.functional_requirements yerine report.parsed_doc.requirements kullanıyoruz
        for req in report.parsed_doc.requirements:
            items_to_process.append({"text": req.text, "meta": "functional"})
        # ----------------------------------
            
        for gap in getattr(report, "gaps", []):
            if isinstance(gap, dict):
                gap_text = f"{gap.get('missing_area')} - {gap.get('suggestion')}"
            else:
                gap_text = str(gap)
            items_to_process.append({"text": gap_text, "meta": "gap"})

        for item in items_to_process:
            try:
                prompt = self._build_prompt(item["text"], language)
                response = self._llm.chat(
                    user_prompt=prompt,
                    metadata={"module": "story_generator", "type": item["meta"]}
                )

                # LLM'den gelen JSON'u temizleyip alıyoruz
                content = response.content.strip()
                if "```json" in content:
                    content = content.split("```json")[1].split("```")[0].strip()
                
                data = json.loads(content)
                stories.append(data)

            except Exception as e:
                # Fallback: Hata durumunda bile boş dönmemesi için güvenli yapı
                fallback_story = "As a User, I want to use this feature, so that I can complete my task" if language == "en" else "Bir Kullanıcı olarak, bu özelliği kullanmak istiyorum, böylece görevimi tamamlayabilirim"
                stories.append({
                    "role": "User",
                    "goal": item["text"],
                    "benefit": "System functionality",
                    "full_story": fallback_story,
                    "acceptance_criteria": ["Requirement implementation check"]
                })

        return stories