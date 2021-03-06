import graphene
from graphene import relay
from graphene_django import DjangoObjectType
from graphene_django.filter import DjangoFilterConnectionField
from graphql_jwt.decorators import login_required
from graphql_relay import from_global_id

from api.models import Employee, Department


class EmployeeNode(DjangoObjectType):
    class Meta:
        model = Employee
        filter_fields = {
            'name': ['exact', 'icontains'],
            'join_year': ['exact', 'icontains'],
            'department__department_name': ['icontains'],
        }
        interfaces = (relay.Node,)


class DepartmentNode(DjangoObjectType):
    class Meta:
        model = Department
        filter_fields = dict()
        filter_fields['employees'] = ['exact']
        filter_fields['department_name'] = ['exact']
        interfaces = (relay.Node,)


class EmployeeCreateMutation(relay.ClientIDMutation):
    class Input:
        name = graphene.String(required=True)
        join_year = graphene.Int(required=True)
        department = graphene.ID(required=True)

    employee = graphene.Field(EmployeeNode)

    @login_required
    def mutate_and_get_payload(root, info, **input):
        employee = Employee(
            name=input.get('name'),
            join_year=input.get('join_year'),
            department_id=from_global_id(input.get('department'))[1]
        )
        employee.save()
        return EmployeeCreateMutation(employee=employee)


class EmployeeUpdateMutation(relay.ClientIDMutation):
    class Input:
        id = graphene.ID(required=True)
        name = graphene.String(required=True)
        join_year = graphene.Int(required=True)
        department = graphene.ID(required=True)

    employee = graphene.Field(EmployeeNode)

    @login_required
    def mutate_and_get_payload(root, info, **input):
        employee = Employee(
            id=from_global_id(input.get('id'))[1]
        )
        employee.name = input.get('name')
        employee.join_year = input.get('join_year')
        employee.department_id = from_global_id(input.get('department'))[1]
        employee.save()
        return EmployeeUpdateMutation(employee=employee)


class EmployeeDeleteMutation(relay.ClientIDMutation):
    class Input:
        id = graphene.ID(required=True)

    employee = graphene.Field(EmployeeNode)

    @login_required
    def mutate_and_get_payload(root, info, **input):
        employee = Employee(
            id=from_global_id(input.get('id'))[1]
        )
        employee.delete()
        return EmployeeDeleteMutation(employee=None)


class DepartmentCreateMutation(relay.ClientIDMutation):
    class Input:
        department_name = graphene.String(required=True)

    department = graphene.Field(DepartmentNode)

    @login_required
    def mutate_and_get_payload(root, info, **input):
        department = Department(
            department_name=input.get('department_name')
        )
        department.save()
        return DepartmentCreateMutation(department=department)


class DepartmentDeleteMutation(relay.ClientIDMutation):
    class Input:
        id = graphene.ID(required=True)

    department = graphene.Field(DepartmentNode)

    @login_required
    def mutate_and_get_payload(root, info, **input):
        department = Department(
            id=from_global_id(input.get('id'))[1]
        )
        department.delete()
        return DepartmentDeleteMutation(department=None)


class Mutation(graphene.AbstractType):
    create_department = DepartmentCreateMutation.Field()
    delete_department = DepartmentDeleteMutation.Field()
    create_employee = EmployeeCreateMutation.Field()
    update_employee = EmployeeUpdateMutation.Field()
    delete_employee = EmployeeDeleteMutation.Field()


class Query(graphene.ObjectType):
    employee = graphene.Field(EmployeeNode, id=graphene.NonNull(graphene.ID))
    all_employees = DjangoFilterConnectionField(EmployeeNode)
    all_departments = DjangoFilterConnectionField(DepartmentNode)

    @login_required
    def resolve_employee(self, info, **kwargs):
        id = kwargs.get('id')
        if id is not None:
            return Employee.objects.get(id=from_global_id(id)[1])

    @login_required
    def resolve_all_employees(self, info, **kwargs):
        return Employee.objects.all()

    @login_required
    def resolve_all_departments(self, info, **kwargs):
        return Department.objects.all()
