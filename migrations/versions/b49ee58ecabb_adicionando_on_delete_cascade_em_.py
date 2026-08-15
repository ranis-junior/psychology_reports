"""adicionando on delete cascade em foreign keys relacionadas a pacientes

Revision ID: b49ee58ecabb
Revises: 944fa16198e2
Create Date: 2026-08-13 19:53:48.602215

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'b49ee58ecabb'
down_revision: Union[str, Sequence[str], None] = '944fa16198e2'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    cascade_fk_constraints()


def downgrade() -> None:
    """Downgrade schema."""
    for table_name, constraint_name, column, referent_table, referent_column in _FK_CONSTRAINTS:
        op.drop_constraint(constraint_name, table_name, type_='foreignkey')
        op.create_foreign_key(
            constraint_name, table_name, referent_table,
            [column], [referent_column],
        )


_FK_CONSTRAINTS = [
    ('idadi_form_question_patient', 'idadi_form_question_patient_id_patient_fkey', 'id_patient', 'patients', 'id'),
    ('patient_records', 'patient_records_id_patient_fkey', 'id_patient', 'patients', 'id'),
    ('pti', 'pti_id_patient_fkey', 'id_patient', 'patients', 'id'),
    ('pti_stimulus_areas', 'pti_stimulus_areas_id_pti_fkey', 'id_pti', 'pti', 'id'),
    ('pti_specific_objectives_topics', 'pti_specific_objectives_topics_id_pti_stimulus_area_fkey',
     'id_pti_stimulus_area', 'pti_stimulus_areas', 'id'),
    ('pti_specific_objectives_subtopics', 'pti_specific_objectives_subto_id_pti_specific_objectives_t_fkey',
     'id_pti_specific_objectives_topics', 'pti_specific_objectives_topics', 'id'),
    ('idadi', 'idadi_id_patient_fkey', 'id_patient', 'patients', 'id'),
    ('idadi_values', 'idadi_values_id_idadi_fkey', 'id_idadi', 'idadi', 'id'),
]


def cascade_fk_constraints() -> None:
    for table_name, constraint_name, column, referent_table, referent_column in _FK_CONSTRAINTS:
        op.drop_constraint(constraint_name, table_name, type_='foreignkey')
        op.create_foreign_key(
            constraint_name, table_name, referent_table,
            [column], [referent_column],
            ondelete='CASCADE',
        )
