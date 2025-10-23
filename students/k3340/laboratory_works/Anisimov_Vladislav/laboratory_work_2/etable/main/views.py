import json
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.http import JsonResponse
from collections import defaultdict
from accounts.models import *
from .models import *

@login_required
def table(request):
    if request.user.user_type != "student":
        user = get_object_or_404(User, username=request.user.username)
        return redirect("/admin")
    else:
        user = get_object_or_404(User, username=request.user.username)
        
        subjects = Subject.objects.filter(classname=user.classname)
        
        selected_subject_id : int = request.GET.get('subject_id')
        selected_subject = None
        assignments = []
        
        if selected_subject_id:
            try:
                selected_subject = subjects.get(id=selected_subject_id)
                assignments = Assignment.objects.filter(subject=selected_subject).order_by('-date_of_issue')
                solutions = Solution.objects.filter(assignment__subject=selected_subject, student=user)    

                solutions_dict = {sol.assignment_id: sol for sol in solutions}

                for assignment in assignments:
                    solution = solutions_dict.get(assignment.id)
                    assignment.link_to_file = solution.link_to_file if solution else None
                    assignment.grade = solution.grade if solution else None
                    
            except Subject.DoesNotExist:
                pass
        
        context = {
            'user': user,
            'subjects': subjects,
            'selected_subject': selected_subject,
            'assignments': assignments,
        }

        return render(request, 'table.html', context)

@login_required
@require_POST
def upload(request):
    try:
        data = json.loads(request.body)
        assignment_id = data.get('assignment_id')
        subject_id = data.get('subject_id')
        file_url = data.get('file_url')
        
        assignment = Assignment.objects.get(id=assignment_id, subject_id=subject_id)
        Solution.objects.create(assignment=assignment,student=request.user,link_to_file=file_url)
                
        return JsonResponse({
            'success': True,
            'message': 'Решение успешно прикреплено'
        })
        
    except Assignment.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': 'Задание не найдено'
        }, status=404)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)

@login_required
def grades(request):
    if request.user.user_type != "student":
        user = get_object_or_404(User, username=request.user.username)
        return redirect("/admin")
    else:
        #data = json.loads(request.body)
        user = get_object_or_404(User, username=request.user.username)
        subjects = Subject.objects.filter(classname=user.classname)
        selected_subject_id : int = request.GET.get('subject_id')
        subject = Subject.objects.get(id=selected_subject_id)
        
        students = User.objects.filter(classname=user.classname, is_staff=False).order_by('full_name')
        
        assignments = Assignment.objects.filter(subject=subject).order_by('date_of_issue')
        
        # Получаем все решения для этих заданий и учеников
        solutions = Solution.objects.filter(assignment__in=assignments, student__in=students).select_related('assignment', 'student')
        student_grades = defaultdict(dict)
        for solution in solutions:
            student_grades[solution.student_id][solution.assignment_id] = {
                'grade': None if solution.grade is None else int(solution.grade),
                'link_to_file': solution.link_to_file
            }
        # Создаем словарь для быстрого доступа: (assignment_id, student_id) -> solution
        grades_data = []
        for student in students:
            student_row = {
                'student': student,
                'grades': []
            }
            for assignment in assignments:
                grade_info = student_grades[student.id].get(assignment.id)
                student_row['grades'].append(grade_info)
            grades_data.append(student_row)
        
        context = {
            'user': user,
            'subjects': subjects,
            'selected_subject': subject,
            'students': students,
            'assignments': assignments,
            'grades_data': grades_data,
        }
        
        return render(request, 'grades.html', context)
