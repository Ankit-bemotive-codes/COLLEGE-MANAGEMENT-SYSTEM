from django.core.management.base import BaseCommand, CommandError

from academics.models import StudentProfile
from fees.models import FeeInvoice, FeeStructure


class Command(BaseCommand):
    help = "Generate a FeeInvoice for every student in a department, for a given FeeStructure."

    def add_arguments(self, parser):
        parser.add_argument("fee_structure_id", type=int)

    def handle(self, *args, **options):
        try:
            fee_structure = FeeStructure.objects.get(pk=options["fee_structure_id"])
        except FeeStructure.DoesNotExist as exc:
            raise CommandError(f"FeeStructure {options['fee_structure_id']} does not exist.") from exc

        students = StudentProfile.objects.filter(
            department=fee_structure.department, semester=fee_structure.semester
        )
        created_count = 0

        for student in students:
            _, created = FeeInvoice.objects.get_or_create(
                student=student,
                fee_structure=fee_structure,
                defaults={"amount_due": fee_structure.amount},
            )
            if created:
                created_count += 1

        self.stdout.write(
            self.style.SUCCESS(
                f"Generated {created_count} new invoice(s) for {fee_structure} "
                f"({students.count()} students in department/semester)."
            )
        )
