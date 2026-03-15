import os
import glob
import time
import nbformat
from google import genai

# ==========================================
# 1. 설정 (Settings)
# ==========================================
# 발급받은 Gemini API 키를 입력하세요.
API_KEY = "발급받은 API KEY"

# 작업할 디렉토리 경로
TARGET_DIR = "/Users/bat/lecture/ClimateLaboratoryBook/courseware_kor"

# 새로운 구글 GenAI 클라이언트 초기화
client = genai.Client(api_key=API_KEY)
# 사용할 모델 지정 (새로운 API 방식)
MODEL_ID = 'gemini-2.5-flash'

# ==========================================
# 2. 번역 함수 정의
# ==========================================
def translate_text_with_gemini(text):
    # 빈 셀이나 너무 짧은 공백은 번역하지 않음
    if not text or len(text.strip()) < 2:
        return text
        
    prompt = f"""
    당신은 기후학, 대기과학, 지구과학 전문 번역가입니다. 
    다음 주어진 마크다운(Markdown) 텍스트를 기후학 전공 학부생들이 이해하기 쉽게 자연스러운 한국어로 번역해주세요.
    
    [중요 지침]
    1. 마크다운 문법(#, *, -, > 등), HTML 태그는 절대 수정하지 말고 그대로 유지하세요.
    2. 수학 수식(LaTeX 문법, $ 또는 $$로 둘러싸인 부분)은 번역하거나 수정하지 말고 원본 그대로 유지하세요.
    3. 코드 블록(``` 로 둘러싸인 부분) 안의 내용은 번역하지 마세요.
    4. 전문 용어(예: Albedo, Radiative Forcing, Insolation 등)는 한국어로 번역하되, 필요한 경우 괄호 안에 영문을 병기해도 좋습니다.
    5. 번역된 텍스트만 출력하고 다른 부연 설명은 하지 마세요.

    [번역할 텍스트]:
    {text}
    """
    
    try:
        # 최신 SDK의 호출 방식 적용
        response = client.models.generate_content(
            model=MODEL_ID,
            contents=prompt,
        )
        return response.text
    except Exception as e:
        print(f"\n[API 에러 발생]: {e}")
        print("잠시 후 다시 시도합니다...")
        time.sleep(10) # 에러 발생 시 잠시 대기
        return text # 실패 시 원본 텍스트 반환 (안전망)

# ==========================================
# 3. 메인 실행부
# ==========================================
def process_notebooks():
    notebook_files = glob.glob(os.path.join(TARGET_DIR, "*.ipynb"))
    
    if not notebook_files:
        print(f"[{TARGET_DIR}] 경로에서 .ipynb 파일을 찾을 수 없습니다.")
        return

    print(f"총 {len(notebook_files)}개의 노트북 파일을 찾았습니다. 번역을 시작합니다...\n")

    for file_path in notebook_files:
        filename = os.path.basename(file_path)
        print(f"처리 중: {filename} ...", end=" ")
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                nb = nbformat.read(f, as_version=4)
            
            translated_cell_count = 0
            
            for cell in nb.cells:
                if cell.cell_type == 'markdown':
                    original_text = cell.source
                    translated_text = translate_text_with_gemini(original_text)
                    
                    if translated_text and translated_text.strip():
                        cell.source = translated_text
                        translated_cell_count += 1
                        
                    # API Rate Limit 방지용 대기
                    #time.sleep(2) 

            with open(file_path, 'w', encoding='utf-8') as f:
                nbformat.write(nb, f)
                
            print(f"완료! ({translated_cell_count}개의 마크다운 셀 번역됨)")
            
        except Exception as e:
            print(f"실패! (에러: {e})")

if __name__ == "__main__":
    process_notebooks()
    print("\n모든 작업이 완료되었습니다!")


