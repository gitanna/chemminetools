# Create your views here.
from django.shortcuts import redirect, render_to_response, render
from django.http  import HttpResponse
from django.template import RequestContext
from guest.decorators import guest_allowed, login_required
from drugbank.models import Drugtargets_distinct_org,Drugtargets_org
import json
import operator
from django.db.models import Q
import openbabel
from pybel import *


def drugbank_lookup(request):
    dict_page = {}

    try:
        drugs = request.GET.get('druglist')
    except:
        drugs = request.POST.get('druglist')
    druglist = []
    if drugs:
        str(drugs).split(",")
        druglist = drugs.split(",")

    if druglist:
        #queryset = Drugtargets_distinct_org.objects.filter(drugbank_id__in=druglist)
        queryset = Drugtargets_org.objects.filter(drugbank_id__in=druglist)

        results = get_results(queryset, 'drugbank_id', request)
    else:
        #queryset = Drugtargets_distinct_org.objects.all()
        queryset = Drugtargets_org.objects.all()
        results = get_results(queryset, 'drugbank_id', request)

    showFields = ['drugbank_id','drug_name','drug_type','uniprot_id','uniprot_name']


    url = '/drugbank/?isajax=true&druglist=' + drugs

    c = {'showFields':showFields, 'url':url}

    if 'isajax' in request.REQUEST:

        dict_page['total'] = results['total']
        dict_page['rows'] = get_rows(showFields, results['results'], int(results['page_number']), int(results['rows_number']))

        result_json = json.dumps(dict_page)

        return HttpResponse(result_json)
    return render_to_response('annotation_5.html',c, context_instance=RequestContext(request) )


def get_results(queryset, sorting_order, request):
    """ Gets data based on the search type and passed parameters

    @param queryset: result query set
    @param sorting_order: string
    @param request: http request
    @return: results

    """

    results = {}
    page_number = 1
    ordering = 'asc'
    rows_number = 10
    offset_number = (page_number - 1) * rows_number
    # sorting
    print '\n in sorting order'
    sorting_order = get_sorting_order(request, sorting_order)
    print '\n finished sorting ', sorting_order

    # filter
    try:
        results['results'] = queryset
    #     results['results'] = self.get_all_filters(request.REQUEST['filterRules'],queryset, sorting_order)
    #     print '\n got all_filters ', results['results']
    except:
        print '\n did not get queryset '
    # paging
    try:
        page_number = request.REQUEST['page']
        ordering = request.REQUEST['order']
        rows_number = request.REQUEST['rows']
        offset_number = (page_number - 1) * rows_number
    except:
        pass
    results['results'] = results['results'].order_by(sorting_order)
    results['ordering'] = ordering
    results['rows_number'] = rows_number
    results['page_number'] = page_number
    results['sorting_order'] = sorting_order
    results['offset_number'] = offset_number
    results['total'] = results['results'].count()
    print '\n what is total? ', results['total']

    return results

def get_results_page(results, page_number, rows_number):

        offset_number = int((int(page_number) - 1)) * int(rows_number)
        beg = int(offset_number)
        end = int(rows_number) + beg

        results_page = results[beg:end]
        return results_page

def get_rows(showFields, results, page_number, rows_number):

        r_list = []
        results_page = get_results_page(results, page_number, rows_number)


        n = 0
        for r in results_page:
            n = n + 1
            r_dict = {}

            for f in showFields:
                print '\n field f is ',
                if str(f) != 'id':
                    r_dict[f] = r.get_field(f)

            drugname = r_dict['drugbank_id']
            r_dict['structure'] = '<img src="https://www.drugbank.ca/structures/' + drugname + '/image.png"  width="160" height="160">'
            r_list.append(r_dict)

        return r_list

def get_range(string, separator):
        return [x.strip() for x in string.split(separator)]

def get_all_filters(filtering, queryset, sorting_order):
        kwargs = {}
        result = queryset
        try:
            filters = json.loads(filtering)

            print '\n filters are now ', filters
            for filter in filters:
                print '\n for filter in filters ', filter

                argument_list = []
                if str(filter["op"]) == 'similar':
                    value_list = get_range(str(filter["value"]), ",")
                    for l in value_list:
                        argument_list.append(Q(**{str(filter['field']) + '__icontains': l}))

                elif str(filter["op"]) == 'equal':
                    # kwargs[str(filter['field'])] = str(filter["value"])
                    value_list = get_range(str(filter["value"]), ",")
                    for l in value_list:
                        print '\n in l is (', l, ')'
                        argument_list.append(Q(**{str(filter['field']) + '__iexact': l}))

                elif str(filter["op"]) == 'notequal':
                    argument_list.append(~Q(**{str(filter['field']) + '__iexact': filter["value"]}))

                elif str(filter["op"]) == 'between':
                    range = get_range(str(filter["value"]), ":")
                    kwargs = {"%s__range" % (str(filter['field'])): (str(range[0]), str(range[1]))}

                elif str(filter["op"]) == 'less':
                    kwargs = {"%s__lt" % (str(filter['field'])): (filter["value"])}
                elif str(filter["op"]) == 'greater':
                    kwargs = {"%s__gt" % (str(filter['field'])): (filter["value"])}
                elif str(filter["op"]) == 'nofilter':
                    try:
                        del kwargs[str(filter['field'])]
                    except:
                        try:
                            del argument_list[str(filter['field'])]
                        except:
                            print '\n was not able to remove filter'

                result = result.filter(**kwargs).order_by(sorting_order)

                result = result.filter(reduce(operator.or_, argument_list))

        except:
            pass
        return result


def get_sorting_order(request,sorting_order):
        ordering = 'asc'

        try:
            sorting_order = request.REQUEST['sort']
            ordering = request.REQUEST['order']

        except:
            pass

        if ordering == 'desc':
            sorting_order = '-'+str(sorting_order)

        return sorting_order

