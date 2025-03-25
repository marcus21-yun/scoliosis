class ExerciseGuide:
    def __init__(self):
        self.exercises = {
            'basic': [
                {
                    'name': '벽 스트레칭',
                    'description': '벽에 등을 대고 서서 양팔을 벽을 따라 천천히 올렸다 내립니다.',
                    'duration': '5분',
                    'difficulty': '초급',
                    'image': 'wall_stretch.jpg'
                },
                {
                    'name': '고양이 자세',
                    'description': '무릎을 대고 엎드린 자세에서 등을 둥글게 말았다 펴는 동작을 반복합니다.',
                    'duration': '3분',
                    'difficulty': '초급',
                    'image': 'cat_pose.jpg'
                }
            ],
            'intermediate': [
                {
                    'name': '코브라 자세',
                    'description': '엎드린 자세에서 상체를 들어올려 척추를 늘립니다.',
                    'duration': '5분',
                    'difficulty': '중급',
                    'image': 'cobra_pose.jpg'
                },
                {
                    'name': '사이드 플랭크',
                    'description': '한쪽 팔꿈치를 대고 몸을 일자로 유지합니다.',
                    'duration': '3분',
                    'difficulty': '중급',
                    'image': 'side_plank.jpg'
                }
            ],
            'advanced': [
                {
                    'name': '브릿지',
                    'description': '누운 자세에서 엉덩이를 들어올려 척추를 늘립니다.',
                    'duration': '5분',
                    'difficulty': '고급',
                    'image': 'bridge.jpg'
                },
                {
                    'name': '슈퍼맨 자세',
                    'description': '엎드린 자세에서 양팔과 양다리를 들어올립니다.',
                    'duration': '3분',
                    'difficulty': '고급',
                    'image': 'superman.jpg'
                }
            ]
        }

    def get_exercises_by_level(self, level):
        return self.exercises.get(level, [])

    def get_exercises_by_curvature(self, curvature):
        if curvature < 0.1:
            return self.exercises['basic']
        elif curvature < 0.2:
            return self.exercises['intermediate']
        else:
            return self.exercises['advanced']

    def get_exercise_program(self, curvature, duration):
        exercises = self.get_exercises_by_curvature(curvature)
        program = []
        
        for exercise in exercises:
            program.append({
                'name': exercise['name'],
                'description': exercise['description'],
                'duration': exercise['duration'],
                'difficulty': exercise['difficulty']
            })
        
        return program 