from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django import forms
from markdown2 import Markdown
import random as RandomInt
from . import util

markdowner = Markdown()


class EntryForm(forms.Form):
    title = forms.CharField(label="Title", widget=forms.TextInput(attrs={'cols': 60}))
    content = forms.CharField(label="Content", widget=forms.Textarea(attrs={'cols': 120}))


def index(request):
    return render(request, "encyclopedia/index.html", {
        "entries": util.list_entries()
    })


def entry(request, title):
    this_entry = util.get_entry(title)
    if this_entry is not None:
        return render(request, "encyclopedia/entry.html", {
            "entry": markdowner.convert(this_entry),
            "title": title
        })
    else:
        return render(request, "encyclopedia/error.html", {
            "title": title
        })


def random(request):
    entries_list = util.list_entries()
    random_title = entries_list[RandomInt.randint(0, len(entries_list) - 1)]
    return HttpResponseRedirect(reverse("entry", kwargs={'title': random_title}))


def new(request):
    if request.method == "POST":
        form = EntryForm(request.POST)
        if form.is_valid():
            title = form.cleaned_data["title"]
            content = form.cleaned_data["content"]
            if title not in util.list_entries():
                util.save_entry(title, content)
                return HttpResponseRedirect(reverse("entry", kwargs={'title': title}))
            else:
                context = {
                    'form': EntryForm(),
                    'message': f"Entry with title {title} already exists."
                }
            return render(request, "encyclopedia/new.html", context)
    else:
        context = {
            'form': EntryForm()
        }
        return render(request, "encyclopedia/new.html", context)


def edit(request, title):
    if request.method == "POST":
        content = request.POST['content']
        util.save_entry(title, content)
        return HttpResponseRedirect(reverse("entry", kwargs={'title': title}))
    else:
        context = {
            "title": title,
            "content": util.get_entry(title)
        }
        return render(request, "encyclopedia/edit.html", context)


def search(request):
    all_entries = util.list_entries()
    title = request.POST["title"]
    if title in all_entries:
        return HttpResponseRedirect(reverse('entry', kwargs={'title': title}))
    else:
        matching_entries = []
        for entry in all_entries:
            if title.lower() in entry.lower():
                matching_entries.append(entry)
        return render(request, "encyclopedia/search.html", {
            "entries": matching_entries,
            "query": title,
            "count": len(matching_entries)
        })
