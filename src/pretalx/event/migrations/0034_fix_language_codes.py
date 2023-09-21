# Generated by Django 4.2.4 on 2023-09-21 10:02
import json

from django.db import migrations
from django.db.models.functions import Lower


def fix_lang_data(lang_data):
    return {key.lower(): value for key, value in lang_data.items()}


def lang_data_needs_fixing(lang_data):
    if isinstance(lang_data, str):
        return False
    if not lang_data:
        return False
    return any(key != key.lower() for key in lang_data.keys())


def fix_language_codes(apps, schema_editor):
    Event = apps.get_model("event", "Event")
    Event_SettingsStore = apps.get_model("event", "Event_SettingsStore")
    User = apps.get_model("person", "User")
    SpeakerInformation = apps.get_model("person", "SpeakerInformation")
    QueuedMail = apps.get_model("mail", "QueuedMail")
    MailTemplate = apps.get_model("mail", "MailTemplate")
    Room = apps.get_model("schedule", "Room")
    Schedule = apps.get_model("schedule", "Schedule")
    TalkSlot = apps.get_model("schedule", "TalkSlot")
    Submission = apps.get_model("submission", "Submission")
    Tag = apps.get_model("submission", "Tag")
    ReviewScoreCategory = apps.get_model("submission", "ReviewScoreCategory")
    Track = apps.get_model("submission", "Track")
    CfP = apps.get_model("submission", "CfP")
    Question = apps.get_model("submission", "Question")
    AnswerOption = apps.get_model("submission", "AnswerOption")
    SubmissionType = apps.get_model("submission", "SubmissionType")

    Event.objects.all().update(
        locale=Lower("locale"),
        locale_array=Lower("locale_array"),
        content_locale_array=Lower("content_locale_array"),
    )
    User.objects.all().update(locale=Lower("locale"))
    Submission.objects.all().update(content_locale=Lower("content_locale"))
    QueuedMail.objects.all().update(locale=Lower("locale"))

    i18nfields = {
        Event: (
            "landing_page_text",
            "featured_sessions_text",
        ),
        MailTemplate: ("subject", "text"),
        Room: ("name", "description", "speaker_info"),
        Schedule: ("comment",),
        TalkSlot: ("description",),
        Tag: ("description",),
        ReviewScoreCategory: ("name",),
        Track: ("name", "description"),
        CfP: ("headline", "text"),
        Question: ("question", "help_text"),
        AnswerOption: ("answer",),
        SubmissionType: ("name",),
        SpeakerInformation: ("title", "text"),
    }

    for model, fields in i18nfields.items():
        update_list = []
        for obj in model.objects.all():
            obj_changed = False
            for field in fields:
                value = getattr(obj, field)
                if value and getattr(value, "data", None):
                    if lang_data_needs_fixing(value.data):
                        value.data = fix_lang_data(value.data)
                        obj_changed = True
            if obj_changed:
                update_list.append(obj)
        if update_list:
            model.objects.bulk_update(update_list, fields=fields)

    update_list = []
    for obj in Event_SettingsStore.objects.filter(
        key="review_help_text", value__isnull=False
    ):
        try:
            lang_data = json.loads(obj.value)
        except Exception:
            continue
        if lang_data_needs_fixing(lang_data):
            obj.value = json.dumps(fix_lang_data(lang_data))
            update_list.append(obj)
    if update_list:
        Event_SettingsStore.objects.bulk_update(update_list, fields=("value",))

    update_list = []
    for cfp in CfP.objects.all():
        if not cfp.settings or "flow" not in cfp.settings or not cfp.settings["flow"]:
            continue

        lang_data = cfp.settings["flow"]
        data_changed = False

        for step_name, step in lang_data["steps"].items():
            for key in ("title", "text"):
                if key in step:
                    if lang_data_needs_fixing(step[key]):
                        step[key] = fix_lang_data(step[key])
                        data_changed = True
            if "fields" in step and step["fields"]:
                for field in step["fields"]:
                    for key in ("label", "help_text", "added_help_text"):
                        if key in field:
                            if lang_data_needs_fixing(field[key]):
                                field[key] = fix_lang_data(field[key])
                                data_changed = True

            lang_data["steps"][step_name] = step
        if data_changed:
            cfp.settings["flow"] = lang_data
            update_list.append(cfp)
    if update_list:
        CfP.objects.bulk_update(update_list, fields=("settings",))


class Migration(migrations.Migration):
    dependencies = [
        ("event", "0033_chinese_locale_codes"),
    ]

    operations = [
        migrations.RunPython(fix_language_codes, migrations.RunPython.noop),
    ]
