from django.core.files.storage import FileSystemStorage
from django.shortcuts import render
from .forms import UserBioForm, UploadFileForm

def process_get_view(request):
    first_name = request.GET.get("first_name", "")
    second_name = request.GET.get("second_name", "")
    person = first_name + second_name
    context = {
        "first_name": first_name,
        "second_name": second_name,
        "person": person
    }
    return render(request, "requestdataapp/request-query-params.html",  context=context)


def user_form(request):
    context = {
        "form": UserBioForm()
    }
    return render(request, "requestdataapp/user-bio-form.html", context=context)


def handle_file_upload(request):
    if request.method == "POST":
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            myfile = form.cleaned_data["file"]
            print(myfile.size)
            if myfile.size > 1048576:
                context = {"volumeerror": "Your file is too big!"}
                return render(request, "requestdataapp/file-upload.html", context=context)
            else:
                context = {"uploadsuccess": "Your file was uploaded successfully"}
                print("File uploading...")
                print(request.FILES)
                fs = FileSystemStorage()
                filename = fs.save(myfile.name, myfile)
                return render(request, "requestdataapp/file-upload.html", context=context)
    else:
        form = UploadFileForm()
    context = {"form": form}
    return render(request, "requestdataapp/file-upload.html", context=context)
