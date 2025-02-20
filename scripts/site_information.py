# Site 클래스 정의
class Site:
    def __init__(self, name, coordinates):
        self.name = name
        self.coordinates = coordinates

    def generate_directory(self, base_path):
        import os
        def create_directory(path):
            import os
            if not os.path.exists(path):  # 디렉토리가 존재하지 않을 경우
                os.makedirs(path)  # 디렉토리 생성
                print(f"Created directory: {path}")  # 생성된 디렉토리 경로 출력
            else:
                return None  # 디렉토리가 존재하면 아무 일도 하지 않는다.

        directory = os.path.join(base_path, self.name)
        create_directory(directory)
        return directory
