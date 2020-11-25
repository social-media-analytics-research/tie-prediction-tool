from random import uniform
import numpy as np
import pandas as pd
import os
from linkprediction.database_connector import DatabaseConnector
import Levenshtein

PERCENTILE_TOP_SIMILAR_COMPETENCES = 80


def default(x, y):
    return 1 if x == y else 0


def _get_occupation_format(attr) -> tuple:
    if isinstance(attr, int):
        return ('job_id', attr)
    if isinstance(attr, str):
        if '>' in attr:
            hierarchy = attr.split('>')
            if hierarchy[-1].isdigit():
                column_type = 'job_id'
            else:
                column_type = 'job_title'
            return (hierarchy[0], hierarchy[1], column_type, hierarchy[2])
        return ('job_title', attr)
    return None


def _choose_correct_hierarchy(u_occupations, v_occupations):
    """ """
    if len(u_occupations) == 0 or len(v_occupations) == 0:
        return None
    u_best_match = next(iter(u_occupations))
    v_best_match = next(iter(v_occupations))
    for u_occupation in u_occupations:
        for v_occupation in v_occupations:
            if u_occupation['subject_area'] == v_occupation['subject_area']:
                return (u_occupation, v_occupation)
            if u_occupation['field_of_activity'] == v_occupation['field_of_activity']:
                u_best_match = u_occupation
                v_best_match = v_occupation
    return (u_best_match, v_best_match)


def _get_competence_similarity(u_competences, v_competences):
    if len(u_competences) == 0 or len(v_competences) == 0:
        return 0
    competence_similarities = []
    for u_competence in u_competences:
        for v_competence in v_competences:
            competence_similarities.append(Levenshtein.ratio(u_competence, v_competence))
    # competence_similarities = sorted(competence_similarities, reverse=True)
    nth_percentile_top_similarities = np.percentile(
        competence_similarities,
        PERCENTILE_TOP_SIMILAR_COMPETENCES,
        axis=0,
        interpolation='nearest'
    )
    similarity_sum = 0
    competence_counter = 0
    for competence_similarity in competence_similarities:
        if competence_similarity >= nth_percentile_top_similarities:
            similarity_sum += competence_similarity
            competence_counter += 1
    return similarity_sum / competence_counter


def occupation_similarity(u_attr: str, v_attr: str):
    db = DatabaseConnector.get_db_instance()
    u_format = _get_occupation_format(u_attr)
    v_format = _get_occupation_format(v_attr)
    if u_format is None or v_format is None:
        raise ValueError('Occupation formatting is wrong!')
    if len(u_format) == 2:
        u_occupations = db.get_occupations_by_column(*u_format)
    else:
        u_occupations = [db.get_occupation_by_hierarchy(*u_format)]
    if len(v_format) == 2:
        v_occupations = db.get_occupations_by_column(*v_format)
    else:
        v_occupations = [db.get_occupation_by_hierarchy(*v_format)]
    u_record, v_record = _choose_correct_hierarchy(u_occupations, v_occupations)
    if u_record['job_id'] == 0 or v_record['job_id'] == 0:
        return 0
    if u_record['job_id'] == v_record['job_id']:
        return 1
    similarity_score = 0
    if u_record['field_of_activity'] == v_record['field_of_activity']:
        similarity_score += 0.3
    if u_record['subject_area'] == v_record['subject_area']:
        similarity_score += 0.3
    similarity_score += 0.4 * _get_competence_similarity(
        u_competences=u_record['competences'],
        v_competences=v_record['competences']
    )
    return similarity_score


def level_of_education_similarity(u_level, v_level):
    """
    Calculate differences between levels in the EQF.

    Graph: https://www.wolframalpha.com/input/?i=1%2F%281%2Bx%29,
    Alternative: https://www.wolframalpha.com/input/?i=e%5E%28-x%29
    """
    if isinstance(u_level, str) or isinstance(v_level, str):
        return default(u_level, v_level)
    return 1 / (1 + abs(u_level - v_level))
