#!/bin/bash

# anaconda(또는 miniconda)가 존재하지 않을 경우 설치해주세요!
## TODO

# conda 실행을 위한 초기화 (스크립트 내에서 conda activate를 쓰기 위함)
eval "$(conda shell.bash hook)" 2> /dev/null

# 1. Conda 존재 여부 확인 및 설치
if ! command -v conda &> /dev/null; then
    echo "Conda not found. Installing Miniconda for Mac..."

    # Mac CPU 아키텍처 확인 (M1/M2/M3 등은 arm64, 인텔맥은 x86_64)
    ARCH=$(uname -m)
    if [ "$ARCH" = "arm64" ]; then
        MINICONDA_URL="https://repo.anaconda.com/miniconda/Miniconda3-latest-MacOSX-arm64.sh"
    else
        MINICONDA_URL="https://repo.anaconda.com/miniconda/Miniconda3-latest-MacOSX-x86_64.sh"
    fi

    # curl 사용 (Mac이라서)
    curl -o miniconda.sh $MINICONDA_URL
    
    # 설치 실행 (-b: 배치모드, -p: 경로지정)
    bash miniconda.sh -b -p $HOME/miniconda
    rm miniconda.sh

    # 설치된 Conda를 현재 세션에 등록
    source $HOME/miniconda/bin/activate
    
    # 다시 한 번 hook 실행하여 conda 명령어 활성화
    eval "$(conda shell.bash hook)"
else 
    echo "[INFO] 기존 Conda 감지"
fi

# Conda 환셩 생성 및 활성화
## TODO
# myenv가 없으면 생성
conda env list | grep myenv > /dev/null || conda create -n myenv python=3.8 -y

echo "[INFO] 'myenv' 가상환경을 활성화합니다..."
conda activate myenv

# Conda 환경 활성화 확인
## 건드리지 마세요! ##
python_env=$(python -c "import sys; print(sys.prefix)")
if [[ "$python_env" == *"/envs/myenv"* ]]; then
    echo "[INFO] 가상환경 활성화: 성공"
else
    echo "[INFO] 가상환경 활성화: 실패"
    exit 1 
fi


# 4. 필요한 패키지 설치
pip install mypy

# 5. Submission 폴더 파일 실행
cd submission || { echo "[INFO] submission 디렉토리로 이동 실패"; exit 1; }

# [중요] output 폴더가 없으면 미리 만들어줍니다!
mkdir -p ../output

echo "[INFO] Python 파일 채점 시작..."

for file in *.py; do
    # 파일이 실제로 존재하는지 확인 (경로 내 py 파일이 없을 경우 대비)
    [ -e "$file" ] || continue

    # 파일명에서 확장자 제거 (.py 제거) -> 변수명을 problem_full_name으로 통일했습니다.
    problem_full_name="${file%.*}"
    
    # 언더바(_) 뒤의 숫자만 추출 (예: 5_3653 -> 3653)
    problem_num="${problem_full_name#*_}"
    
    echo "[INFO] 실행 중: $file (문제 번호: $problem_num)"

    # 입력/출력 파일 경로 확인 후 실행
    if [ -f "../input/${problem_num}_input" ]; then
        # 변수명 오타 수정됨
        python "$file" < "../input/${problem_num}_input" > "../output/${problem_num}_output"
    else
        echo "[WARN] 입력 파일이 없습니다: ../input/${problem_num}_input"
    fi
done

# 6. mypy 테스트 실행 및 로그 저장
echo "[INFO] mypy 테스트 실행 중..."
mypy . > ../mypy_log.txt

# 7. conda.yml 파일 생성
echo "[INFO] 환경 내보내기 중..."
conda env export > ../conda.yml

# 8. 가상환경 비활성화
conda deactivate

echo "[INFO] 모든 작업이 완료되었습니다."