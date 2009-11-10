from django.contrib.contenttypes.models import ContentType
from django.contrib.admin.models import LogEntry
from django.contrib.admin.models import ADDITION, CHANGE, DELETION
from django.utils.encoding import force_unicode

__all__ = ['save_and_log','delete_and_log']


def save_and_log(obj, user, msg = '', flag = None):
    '''
    Shortcut function for saving a model and log the action
    in the LogEntry table
    '''
    if flag == None:
        flag = CHANGE
        if obj._get_pk_val() is None:
            flag = ADDITION
    obj.save()
    dolog(obj,user,flag,msg)


def delete_and_log(obj, user, msg=''):
    re = dolog(obj,user,DELETION,msg)
    obj.delete()


def dolog(obj,user,flag,msg):
    '''
    Log an action into the database.
    Return a 3-elements tuple a
        a[0] is True if everything is fine otherwise the error will be in a[2]
        a[1] is the object to be logged
    '''
    pk_value = obj._get_pk_val()
    model    = obj.__class__
    id       = user.id
    LogEntry.objects.log_action(id,
                                ContentType.objects.get_for_model(model).id,
                                pk_value,
                                force_unicode(obj),
                                flag,
                                msg)
    return True