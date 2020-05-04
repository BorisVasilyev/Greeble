from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.template import loader
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from django.core.files.storage import FileSystemStorage
from django.db.models import Max

import json
import logging
import sys
import csv
import pathlib

from .models import Course, Slide, UserSlideView, Client, Catalogue, Item, ItemProperty, ItemPropertyValue, \
    TestType, Test, UserTestResult, UserCourseStatus
from django.contrib.auth.models import User

logger = logging.getLogger(__name__)


@login_required
def home(request):
    template = loader.get_template('lms/home.html')

    course_in_progress_list = Course.objects.filter(usercoursestatus__user_id=request.user.id,
                                                    usercoursestatus__course_is_in_progress=True).all()

    available_course_list = Course.objects.all()

    context = {
        'course_in_progress_list': course_in_progress_list,
        'available_course_list': available_course_list
    }

    context = add_context_global_vars(context, request.user)

    return HttpResponse(template.render(context, request))


@login_required
def my_courses(request):
    template = loader.get_template('lms/my_courses.html')

    published_course_list = Course.objects.filter(created_by_user_id=request.user.id).filter(status__name='published')

    draft_course_list = Course.objects.filter(created_by_user_id=request.user.id).filter(status__name='editing')

    # completed_course_list = Course.objects.filter(usercoursestatus__user_id=request.user.id,
    #                                              usercoursestatus__course_is_completed=True).all()

    # for course in course_list:
    #    course.is_completed = check_if_course_completed(course.id, request.user.id)

    context = {
        'published_course_list': published_course_list,
        'draft_course_list': draft_course_list
    }

    context = add_context_global_vars(context, request.user)

    return HttpResponse(template.render(context, request))


# @login_required
def view_course(request, course_id):
    template = loader.get_template('lms/course_details.html')

    course = Course.objects.get(id=course_id)

    course_list = Course.objects.all()

    slide_list = course.slide_set.all()

    first_slide_id = 0

    if slide_list.count() != 0:
        first_slide_id = slide_list.filter(previous_slide_id=0).first().id

    creator = User.objects.get(id=course.created_by_user_id)

    # TODO: Change to dynamic link generation
    course_link = 'http://127.0.0.1:8000/lms/course/' + str(course.id)

    context = {
        'course': course,
        'slide_list': slide_list,
        'course_list': course_list,
        'first_slide_id': first_slide_id,
        'creator_user_name': creator.username,
        'course_status': course.status.name,
        'course_link': course_link
    }

    if course.modified_by_user_id:
        modifier = User.objects.get(id=course.modified_by_user_id)
        context['modifier_user_name'] = modifier.username

    context = add_context_global_vars(context, request.user)

    return HttpResponse(template.render(context, request))


@login_required
def publish_course(request, course_id):
    # Validate if user is the author

    course = Course.objects.get(id=course_id)

    if course.created_by_user_id == request.user.id:
        course = Course.objects.get(id=course_id)

        course.status_id = 2  # status = published

        course.save()

    return HttpResponseRedirect("/lms/course/" + str(course_id) + "/")


def render_slide(slide, course, is_course_completed, request):
    previous_slide_id = slide.previous_slide_id
    next_slide_id = slide.next_slide_id

    max_slides = course.slide_set.count()

    slide_list = Slide.objects.filter(course_id=course.id).all()

    context = {
        'course': course,
        'slide': slide,
        'slide_list': slide_list,
        'next_slide_id': next_slide_id,
        'previous_slide_id': previous_slide_id,
        'max_slides': max_slides,
        'is_course_completed': is_course_completed
    }

    context = add_context_global_vars(context, request.user)

    template = loader.get_template('lms/slide_view.html')

    return HttpResponse(template.render(context, request))


def render_test(slide, course, is_course_completed, request):
    previous_slide_id = slide.previous_slide_id
    next_slide_id = slide.next_slide_id

    max_slides = course.slide_set.count()

    test = slide.test
    answers = json.loads(slide.test.content)

    slide_list = Slide.objects.filter(course_id=course.id).all()

    context = {
        'course': course,
        'slide': slide,
        'slide_list': slide_list,
        'test': test,
        'next_slide_id': next_slide_id,
        'previous_slide_id': previous_slide_id,
        'max_slides': max_slides,
        'answers_list': answers['answers'],
        'is_course_completed': is_course_completed
    }

    context = add_context_global_vars(context, request.user)

    template = loader.get_template('lms/question_view.html')

    return HttpResponse(template.render(context, request))


@login_required
def view_slide(request, course_id, slide_id):
    # Record user viewing the slide
    if request.user.is_authenticated:
        current_user_id = request.user.id

        # Check if the user has already viewed this slide.
        # If yes, update last view time.
        # If not, insert a new record.

        existing_slide_view = UserSlideView.objects.filter(user_id=current_user_id, slide_id=slide_id).first()

        if existing_slide_view is not None:
            existing_slide_view.last_view_time = timezone.now()
            existing_slide_view.save()
        else:
            slide_view = UserSlideView(
                user_id=current_user_id,
                slide_id=slide_id,
                last_view_time=timezone.now()
            )

            slide_view.save()

        # Check if there is a record about the course in progress
        # If yes, update the status time
        # If not, insert a new record.

        existing_course_status = UserCourseStatus.objects.filter(user_id=current_user_id, course_id=course_id).first()

        if existing_course_status is not None:
            existing_course_status.updated_time = timezone.now()
            existing_course_status.course_is_in_progress = True
            existing_course_status.save()
        else:
            course_status = UserCourseStatus(
                user_id=current_user_id,
                course_id=course_id,
                course_is_in_progress=True,
                course_is_completed=False,
                updated_time=timezone.now()
            )

            course_status.save()

    course = Course.objects.get(id=course_id)
    slide = course.slide_set.filter(id=slide_id).first()

    # Check if the course has been completed to show the "Finish Course" button
    is_course_completed = check_if_course_is_completed(course_id, current_user_id)

    if slide.type.code == 'slide':
        response = render_slide(slide, course, is_course_completed, request)
    elif slide.type.code == 'test':
        response = render_test(slide, course, is_course_completed, request)
    else:
        response = HttpResponseRedirect("/lms/course/" + str(course_id) + "/")

    return response


@login_required
def edit_course(request, course_id):
    template = loader.get_template('lms/course_edit.html')

    course = Course.objects.get(id=course_id)

    slide_list = course.slide_set.all()

    context = {
        'course': course,
        'slide_list': slide_list
    }

    context = add_context_global_vars(context, request.user)

    return HttpResponse(template.render(context, request))


@login_required
def save_course(request, course_id):
    course = Course.objects.get(id=course_id)

    new_course_name = request.POST['course_name']
    new_course_description = request.POST['course_description']

    course.name = new_course_name
    course.description = new_course_description
    course.last_modified_time = timezone.now()
    course.modified_by_user_id = request.user.id
    course.status_id = 1  # status = editing

    # Parse loaded file
    if request.FILES['input_file']:
        myfile = request.FILES['input_file']

        fs = FileSystemStorage(location='upload/course/cover')

        # Generate a new filename with the same suffix
        new_file_name = 'course_cover_' + str(course.id) + pathlib.Path(myfile.name).suffix

        filename = fs.save(new_file_name, myfile)
        course.cover_filename = filename

    course.save()

    return HttpResponseRedirect("/lms/course/" + str(course_id) + "/")


@login_required
def remove_course(request, course_id):
    course = Course.objects.get(id=course_id)

    course.delete()

    return HttpResponseRedirect("/lms/my_courses")


@login_required
def new_course(request):
    template = loader.get_template('lms/course_new.html')

    context = {}

    context = add_context_global_vars(context, request.user)

    return HttpResponse(template.render(context, request))


@login_required
def add_course(request):
    course_name = request.POST['course_name']
    course_description = request.POST['course_description']

    new_course = Course(name=course_name,
                        description=course_description,
                        publication_time=timezone.now(),
                        client_id=get_user_client_id(request.user),
                        created_by_user_id=request.user.id,
                        created_time=timezone.now(),
                        status_id=1)  # status="editing"

    new_course.save()

    # Parse loaded file
    if request.FILES['input_file']:
        myfile = request.FILES['input_file']

        fs = FileSystemStorage(location='upload/course/cover')

        # Generate a new filename with the same suffix
        new_file_name = 'course_cover_' + str(new_course.id) + pathlib.Path(myfile.name).suffix

        filename = fs.save(new_file_name, myfile)

        new_course.cover_filename = filename
        new_course.save()

    return HttpResponseRedirect("/lms/my_courses")


@login_required
def new_slide(request, course_id):
    template = loader.get_template('lms/slide_new.html')

    course = Course.objects.get(id=course_id)
    slide_list = Slide.objects.filter(course_id=course_id)

    context = {
        'course': course,
        'slide_list': slide_list
    }

    context = add_context_global_vars(context, request.user)

    return HttpResponse(template.render(context, request))


@login_required
def add_slide(request, course_id):
    new_slide_name = request.POST['slide_name']
    new_slide_content = request.POST['slide_content']
    prev_slide_id = request.POST.get('previous_slide_id', 0)

    new_slide = Slide(course_id=course_id,
                      name=new_slide_name,
                      type_id=1,  # type = slide
                      previous_slide_id=prev_slide_id,
                      content=new_slide_content,
                      created_by_user_id=request.user.id,
                      created_time=timezone.now())

    new_slide.save()

    if prev_slide_id != 0:
        prev_slide = Slide.objects.get(id=prev_slide_id)
        prev_slide.next_slide_id = new_slide.id

        prev_slide.save()

    return HttpResponseRedirect("/lms/course/" + str(course_id) + "/edit/")


@login_required
def edit_slide(request, course_id, slide_id):
    template = loader.get_template('lms/slide_edit.html')

    course = Course.objects.get(id=course_id)

    slide = course.slide_set.filter(id=slide_id).first()
    slide_list = Slide.objects.filter(course_id=course_id)

    context = {
        'course': course,
        'slide': slide,
        'slide_list': slide_list
    }

    context = add_context_global_vars(context, request.user)

    return HttpResponse(template.render(context, request))


@login_required
def remove_slide(request, course_id, slide_id):
    slide = Slide.objects.get(id=slide_id)

    if slide.previous_slide_id != 0:
        previous_slide = Slide.objects.get(id=slide.previous_slide_id)
        previous_slide.next_slide_id = slide.next_slide_id
        previous_slide.save()

    if slide.next_slide_id != 0:
        next_slide = Slide.objects.get(id=slide.next_slide_id)
        next_slide.previous_slide_id = slide.previous_slide_id
        next_slide.save()

    slide.delete()

    return HttpResponseRedirect("/lms/course/" + str(course_id) + "/edit/")


@login_required
def save_slide(request, course_id, slide_id):
    course = Course.objects.get(id=course_id)
    slide = course.slide_set.filter(id=slide_id).first()

    new_slide_name = request.POST['slide_name']
    new_slide_content = request.POST['slide_content']
    prev_slide_id = request.POST.get('previous_slide_id', 0)
    next_slide_id = request.POST.get('next_slide_id', 0)

    slide.name = new_slide_name
    slide.content = new_slide_content
    slide.previous_slide_id = prev_slide_id
    slide.next_slide_id = next_slide_id
    slide.modified_by_user_id = request.user.id
    slide.last_modified_time = timezone.now()

    slide.save()

    return HttpResponseRedirect("/lms/course/" + str(course_id) + "/edit/")


@login_required
@csrf_exempt
def validate_answer(request):
    received_json_data = json.loads(request.body)

    test_id = received_json_data['cur_test_id']
    answer_id = received_json_data['cur_answer_id']

    test = Test.objects.get(id=test_id)

    answers = json.loads(test.content)

    is_answer_correct = False
    points = 0

    for answ in answers['answers']:
        if answ["answer_index"] == answer_id and answ["answer_is_correct"] is True:
            is_answer_correct = True
            points = test.max_points

    if is_answer_correct:
        # Check the answer history and update
        answer_exists = (UserTestResult.objects.filter(user_id=request.user.id).filter(test_id=test.id).count() > 0)

        if not answer_exists:
            test_result = UserTestResult(
                test_id=test.id,
                user_id=request.user.id,
                points=points,
                last_pass_time=timezone.now()
            )

            test_result.save()

    explanation = ''

    if is_answer_correct:
        explanation = answers['answer_explanation']

    response = "false"
    if is_answer_correct == 1:
        response = "true"

    # Check whether the course is completed to show the "Finish course" button
    slide = Slide.objects.filter(test_id=test_id).first()

    is_course_completed = check_if_course_is_completed(slide.course_id, request.user.id)

    return JsonResponse({'result': response, 'is_course_completed': is_course_completed, 'answer_explanation': explanation})


def logout_view(request):
    logout(request)

    return HttpResponseRedirect("/lms/login")


@login_required
def statistics(request):
    template = loader.get_template('lms/statistics.html')

    user_slide_view_list = UserSlideView.objects.all()

    for user_slide_view in user_slide_view_list:
        user_slide_view.user_name = User.objects.get(id=user_slide_view.user_id).username

        slide = Slide.objects.get(id=user_slide_view.slide_id)

        user_slide_view.slide_name = slide.name
        user_slide_view.course_name = Course.objects.get(id=slide.course_id).name

    context = {
        'user_slide_view_list': user_slide_view_list
    }

    context = add_context_global_vars(context, request.user)

    return HttpResponse(template.render(context, request))


@login_required
def administration(request):
    template = loader.get_template('lms/administration.html')

    user_list = User.objects.all()

    context = {
        'user_list': user_list
    }

    context = add_context_global_vars(context, request.user)

    return HttpResponse(template.render(context, request))


@login_required
def settings(request):
    template = loader.get_template('lms/settings.html')

    context = {}

    context = add_context_global_vars(context, request.user)

    return HttpResponse(template.render(context, request))


@login_required
def catalogues(request):
    template = loader.get_template('lms/catalogues.html')

    cur_client_id = get_user_client_id(request.user)

    if cur_client_id != 0:
        catalogue_list = Catalogue.objects.filter(client_id=cur_client_id)

        context = {
            'catalogue_list': catalogue_list
        }

    context = add_context_global_vars(context, request.user)

    return HttpResponse(template.render(context, request))


@login_required
def new_catalogue(request):
    template = loader.get_template('lms/catalogue_new.html')

    context = {}

    context = add_context_global_vars(context, request.user)

    return HttpResponse(template.render(context, request))


@login_required
def add_catalogue(request):
    catalogue_name = request.POST['catalogue_name']
    catalogue_desc = request.POST['catalogue_desc']
    name_column = request.POST['name_column']
    desc_column = request.POST['description_column']

    write_log_msg('Name column: "' + name_column + '"')
    write_log_msg('Description column: "' + desc_column + '"')

    cat = Catalogue(name=catalogue_name,
                    description=catalogue_desc,
                    client_id=get_user_client_id(request.user))

    cat.save()

    # Parse loaded file
    if request.FILES['input_file']:
        myfile = request.FILES['input_file']
        fs = FileSystemStorage()
        filename = fs.save(myfile.name, myfile)

        file_path = fs.path(filename)

        write_log_msg('Parsing file: "' + file_path + '"')

        csv.register_dialect('myDialect',
                             delimiter=',',
                             skipinitialspace=True)

        csv_file = open(file_path, 'r')
        reader = csv.DictReader(csv_file, dialect='myDialect')

        file_columns = reader.fieldnames

        write_log_msg('Column names: ' + ''.join(file_columns))

        # Save columns as ItemProperty objects to the database

        column_ids = {}

        for file_col in file_columns:

            if file_col != name_column.strip() and file_col != desc_column.strip():
                col = ItemProperty(name=file_col.strip(),
                                   catalogue_id=cat.id)

                col.save()

                column_ids[file_col.strip()] = col.id

        # For each row, save it to the database as Items as ItemPropertyValue objects
        row_num = 1

        for row in reader:
            row_str = ''

            it = Item(catalogue_id=cat.id,
                      name=row[name_column],
                      description=row[desc_column],
                      created_time=timezone.now(),
                      created_by_user_id=get_user_client_id(request.user))

            it.save()

            for col in file_columns:
                if col.strip() != name_column and col.strip() != desc_column:
                    ipv = ItemPropertyValue(item_id=it.id,
                                            item_property_id=column_ids[col.strip()],
                                            value=row[col].strip())

                    ipv.save()

                    row_str += col + '=' + row[col].strip() + ' '

            write_log_msg('Row #' + str(row_num) + ': ' + row_str)

            row_num += 1

    # Redirect to the newly created catalogue's page

    return HttpResponseRedirect("/lms/catalogue/" + str(cat.id))


@login_required
def view_catalogue(request, catalogue_id):
    write_log_msg('Entering view_catalogue')

    template = loader.get_template('lms/catalogue_view.html')

    cat = Catalogue.objects.get(id=catalogue_id)

    item_list = Item.objects.filter(catalogue_id=cat.id)

    item_count = item_list.count()

    item_properties_list = ItemProperty.objects.filter(catalogue_id=cat.id)

    for item in item_list:
        properties_values = ''

        for item_property in item_properties_list:
            property_value = ItemPropertyValue.objects.filter(item_id=item.id).get(item_property_id=item_property.id).value

            properties_values += item_property.name + ': ' + property_value + '\n'

        item.properties_values = properties_values

    context = {
        'catalogue': cat,
        'item_list': item_list,
        'item_count': item_count
    }

    context = add_context_global_vars(context, request.user)

    return HttpResponse(template.render(context, request))


def is_user_client_content_manager(user):
    return user.groups.filter(name='client-content-managers').exists()


def is_user_client_admin(user):
    return user.groups.filter(name='client-administrators').exists()


def get_user_company_name(user):
    user_groups = user.groups.all()

    clients = Client.objects.all()

    result = ''

    for user_group in user_groups:
        for client in clients:
            if user_group.id == client.users_group.id:
                result = client.name

    return result


def get_user_client_id(user):
    user_groups = user.groups.all()

    clients = Client.objects.all()

    result = ''

    for user_group in user_groups:
        for client in clients:
            if user_group.id == client.users_group.id:
                result = client.id

    return result


def add_context_global_vars(dict, user):
    company_name = get_user_company_name(user)

    user_is_content_manager = is_user_client_content_manager(user)
    user_is_client_admin = is_user_client_admin(user)

    dict['company_name'] = company_name
    dict['user_is_content_manager'] = user_is_content_manager
    dict['user_is_client_admin'] = user_is_client_admin

    return dict


def write_log_msg(message):
    print('[debug] ' + str(message), file=sys.__stderr__)

    logger.info(str(message))


@login_required
def new_test(request, course_id):
    template = loader.get_template('lms/test_new.html')

    test_types = TestType.objects.all()

    course = Course.objects.get(id=course_id)

    context = {
        'test_type_list': test_types,
        'course': course
    }

    context = add_context_global_vars(context, request.user)

    return HttpResponse(template.render(context, request))


@login_required
def add_test(request, course_id):
    # Prepare test JSON
    question_caption = request.POST['question_caption']
    question_content = request.POST['question_content']

    answers = []
    answ_index = 1

    while ('answ_text_' + str(answ_index)) in request.POST:
        answ_dict = {}

        answ_dict["answer_index"] = str(answ_index)
        answ_dict["answer_is_correct"] = (request.POST['answ_radio'] == 'answ_radio_' + str(answ_index))
        answ_dict["answer_text"] = request.POST['answ_text_' + str(answ_index)]

        answers.append(answ_dict)

        answ_index += 1

    answers_json = json.dumps({'answer_explanation': request.POST['answer_explanation'], 'answers': answers})

    # Create a new test
    test = Test(
        content=answers_json,
        max_points=1,
        created_time=timezone.now(),
        created_by_user_id=get_user_client_id(request.user),
        type_id=1
    )

    test.save()

    # Get maximum slide ID
    previous_slide_id = Slide.objects.filter(course_id=course_id).aggregate(Max('id'))['id__max']

    if previous_slide_id is None:
        previous_slide_id = 0

    # Create a new slide with type "test"
    new_slide = Slide(course_id=course_id,
                      name=question_caption,
                      content=question_content,
                      type_id=2,
                      previous_slide_id=previous_slide_id,
                      next_slide_id=0,
                      test_id=test.id,
                      created_time=timezone.now(),
                      created_by_user_id=get_user_client_id(request.user)
    )

    new_slide.save()

    # Update the previous slide
    if previous_slide_id != 0:
        previous_slide = Slide.objects.get(id=previous_slide_id)

        if previous_slide is not None:
            previous_slide.next_slide_id = new_slide.id
            previous_slide.save()

    return HttpResponseRedirect("/lms/course/" + str(course_id) + "/edit/")


@login_required
def edit_test(request, course_id, slide_id):
    template = loader.get_template('lms/question_edit.html')

    course = Course.objects.get(id=course_id)

    question = course.slide_set.filter(id=slide_id).first()

    slide_list = Slide.objects.filter(course_id=course_id)

    answers_list = Answer.objects.filter(slide_id=slide_id)

    answer_list_string = ""
    current_answer_no = 0
    correct_answer_no = 0

    for answer in answers_list:
        answer_list_string += answer.text + "\n"
        current_answer_no += 1

        if answer.is_correct == 1:
            correct_answer_no = current_answer_no

    context = {
        'course': course,
        'question': question,
        'answers': answer_list_string,
        'correct_answer_num': correct_answer_no,
        'slide_list': slide_list
    }

    context = add_context_global_vars(context, request.user)

    return HttpResponse(template.render(context, request))


@login_required
def save_test(request, course_id, slide_id):
    question_name = request.POST['question_name']
    question_content = request.POST['question_content']
    answers_raw_text = request.POST['question_answers']
    correct_answer_no = request.POST['correct_answer_num']
    previous_slide_id = request.POST['previous_slide_id']

    slide = Slide.objects.get(id=slide_id)

    slide.name = question_name
    slide.content = question_content
    slide.previous_slide_id = previous_slide_id

    slide.save()

    answers_list = Answer.objects.filter(slide_id=slide_id)

    for answer in answers_list:
        answer.delete()

    answers_text_list = answers_raw_text.splitlines()

    for idx, answer_text in enumerate(answers_text_list, start=1):
        if idx == int(correct_answer_no):
            is_correct_answer = 1
        else:
            is_correct_answer = 0

        new_answer = Answer(slide_id=slide.id,
                            text=answer_text,
                            is_correct=is_correct_answer)

        new_answer.save()

    return HttpResponseRedirect("/lms/course/" + str(course_id) + "/edit/")


def check_if_course_is_completed(course_id, user_id) -> bool:
    # True if the user has viewed all the slides in the course and completed all the tests, otherwise False

    res = True

    slides = Slide.objects.filter(course_id=course_id).all()

    for s in slides:
        # Check if the slide has been viewed
        if UserSlideView.objects.filter(user_id=user_id, slide_id=s.id).count() == 0:
            res = False

        # If the slide is a test, check whether the test has been completed
        if s.type.code == 'test' \
                and UserTestResult.objects.filter(test_id=s.test_id, user_id=user_id).count() == 0:
            res = False

    return res


@login_required
def finish_course(request, course_id):
    # Check again if the course has been completed

    if check_if_course_is_completed(course_id, request.user.id):
        # Check whether a record in UserCourseStatus already exists

        user_course_status = UserCourseStatus.objects.filter(course_id=course_id, user_id=request.user.id).first()

        if user_course_status is not None:
            user_course_status.course_is_completed = True
            user_course_status.course_is_in_progress = False
            user_course_status.updated_time = timezone.now()
            user_course_status.save()
        else:
            new_status = UserCourseStatus(user_id=request.user.id,
                                          course_id=course_id,
                                          course_is_in_progress=False,
                                          course_is_completed=True,
                                          updated_time=timezone.now())
            new_status.save()

    return HttpResponseRedirect("/lms")
