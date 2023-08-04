from django.shortcuts import render


def home_page(request):
    data={
        'title':"TamTumba"
    }
    return render(request,'main/main.html',data)
