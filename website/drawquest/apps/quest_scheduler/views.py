from django.shortcuts import get_object_or_404

from canvas.view_guards import require_staff
from canvas.shortcuts import r2r_jinja
from drawquest.apps.quest_scheduler.models import QuestPreview, suggested_quests, scheduled_quest_previews
from drawquest.apps.quests.models import ScheduledQuest, Quest


@require_staff
def schedule(request):
    page_updated = False

    if request.method == 'POST':
        ordinals = {}
        for key, ordinal in request.POST.iteritems():
            if 'sort_order' not in key:
                continue

            _, id_ = key.split('-')
            quest = get_object_or_404(Quest, id=id_)

            if ordinal is None or not str(ordinal).strip():
                try:
                    quest = ScheduledQuest.objects.get(quest=quest)
                    quest.delete()
                except ScheduledQuest.DoesNotExist:
                    pass
                continue

            try:
                ordinal = int(ordinal)
            except ValueError:
                ordinal = 0

            quest.schedule(ordinal, curator=request.user)

        page_updated = True

    ctx = {
        'scheduled_quests': scheduled_quest_previews(),
        'suggested_quests': suggested_quests(),
        'current_scheduled_quest': QuestPreview.get_from_scheduled_quest(ScheduledQuest.current_scheduled_quest()),
        'page_updated': page_updated,
    }
    return r2r_jinja('quests/schedule.html', ctx, request)

