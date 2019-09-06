from auto_class.intermediate_representation import Type, Sequence, HashTable, DataClass, Member


def test_classes_and_attributes(ir_test_data):
    """This test creates a variety of intermediate represntation objects with different attributes set and asserts that
    object creating does not rasie exceptions
    This is a regression test to ensure that all intermediate representation object names and attributes tested here
    continue to exists in the future.
    auto_class frontends and backends depend on the intermediate representation objects to be stable and consistent"""
    assert ir_test_data.type_scalars
    assert ir_test_data.type_sequences
    assert ir_test_data.type_hashtables
    assert ir_test_data.members
    assert ir_test_data.dataclasses
    assert ir_test_data.complete_dataclass_example
