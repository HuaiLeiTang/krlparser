#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pytest

from krlparser.parser import Parser
from krlparser.ast import (Module, SourceFile, DataFile, FileAttribute,
                           FunctionDefinition, DataDefinition, Parameter, Type,
                           FunctionCall, VariableSymbol)
from krlparser.exceptions import ParsingError


def test_module_parsing():
    module_name = "Foo"

    source_file = (
        "GLOBAL DEF Foo(bar:IN, foobar:OUT)\n"
        "\n"
        "END"
        "\n"
        "\n"
        "DEF Bar()\n"
        "\n"
        "END"
    )

    data_file = (
        "DEFDAT Foo\n"
        "\n"
        "ENDDAT"
    )

    awaited_ast = [
        Module(name=module_name,
               source_file=SourceFile(name=module_name, statements=[
                   FunctionDefinition(name="Foo", parameters=[
                       Parameter(name="bar",
                                 parameter_type=Parameter.TYPE.IN),
                       Parameter(name="foobar",
                                 parameter_type=Parameter.TYPE.OUT)],
                       is_global=True),
                   FunctionDefinition(name="Bar")]),
               data_file=DataFile(name=module_name,
                                  statements=[DataDefinition(name="Foo")])
               )]

    parser = Parser()
    parser.add_module(module_name, source_file, data_file)

    assert awaited_ast == parser.ast


def test_source_parsing():
    source_file = (
        "GLOBAL DEF Foo(bar:IN, foobar:OUT)\n"
        "\n"
        "END"
        "\n"
        "\n"
        "DEF Bar()\n"
        "\n"
        "END"
    )

    awaited_ast = [
        SourceFile(name="Foo", statements=[
            FunctionDefinition(name="Foo", parameters=[
                Parameter(name="bar", parameter_type=Parameter.TYPE.IN),
                Parameter(name="foobar", parameter_type=Parameter.TYPE.OUT)
            ], is_global=True),
            FunctionDefinition(name="Bar")
        ])]

    parser = Parser()
    parser.add_source_file("Foo", source_file)

    assert awaited_ast == parser.ast


def test_data_parsing():
    data_file = (
        "DEFDAT Foo\n"
        "\n"
        "ENDDAT"
    )

    awaited_ast = [DataFile(name="Foo",
                            statements=[DataDefinition(name="Foo")])]

    parser = Parser()
    parser.add_data_file("Foo", data_file)

    assert awaited_ast == parser.ast


def test_sub_parsing():
    pass


def test_mod_call():
    source_file = (
        "DEF Foo()\n"
        "Bar(foo, bar)\n"
        "FooBar()\n"
        "END"
        "\n"
        "DEF Bar(foo:IN, bar:IN)\n"
        "END"
        "\n"
        "DEF FooBar()\n"
        "END"
    )

    awaited_ast = [
        SourceFile(name="Foo", statements=[
            FunctionDefinition(name="Foo", body=[
                FunctionCall(name="Bar", parameters=["foo", "bar"]),
                FunctionCall(name="FooBar")
            ]),
            FunctionDefinition(name="Bar", parameters=[
                Parameter(name="foo", parameter_type=Parameter.TYPE.IN),
                Parameter(name="bar", parameter_type=Parameter.TYPE.IN)
            ]),
            FunctionDefinition(name="FooBar")])]

    parser = Parser()
    parser.add_source_file("Foo", source_file)

    assert awaited_ast == parser.ast


def test_file_attributes():
    source_file = (
        "&COMMENT Hello\n"
        "DEF Foo()\n"
        "END"
    )

    awaited_ast = [
        SourceFile(name="Foo",
                   file_attributes=[FileAttribute(value="COMMENT Hello")],
                   statements=[FunctionDefinition(name="Foo")])]

    parser = Parser()
    parser.add_source_file("Foo", source_file)

    assert awaited_ast == parser.ast


def test_source_file_without_definition():
    source_file = (
        "&COMMENT Hello\n"
    )

    parser = Parser()
    with pytest.raises(ParsingError):
        parser.add_source_file("Foo", source_file)


def test_data_file_without_definition():
    data_file = (
        "&COMMENT Hello\n"
    )

    parser = Parser()
    with pytest.raises(ParsingError):
        parser.add_data_file("Foo", data_file)


def test_data_file_with_multiple_definitions():
    data_file = (
        "DEFDAT Foo\n"
        "\n"
        "ENDDAT"
        "\n"
        "DEFDAT Foo\n"
        "\n"
        "ENDDAT"
    )

    parser = Parser()
    with pytest.raises(ParsingError):
        parser.add_data_file("Foo", data_file)


def test_source_file_with_single_function():
    source_file = (
        "DEFFCT INT Foo(bar:IN, foobar:OUT)\n"
        "\n"
        "ENDFCT"
    )

    awaited_ast = [
        SourceFile(name="Foo", statements=[
            FunctionDefinition(name="Foo", parameters=[
                Parameter(name="bar", parameter_type=Parameter.TYPE.IN),
                Parameter(name="foobar", parameter_type=Parameter.TYPE.OUT)
            ], returns=Type(name="INT"))])]

    parser = Parser()
    parser.add_source_file("Foo", source_file)

    assert awaited_ast == parser.ast


def test_module_with_invalid_parameter_type():
    source_file = (
        "DEFFCT INT Foo(bar:invalid)\n"
        "\n"
        "ENDFCT"
    )

    parser = Parser()
    with pytest.raises(ParsingError):
        parser.add_source_file("Foo", source_file)


def test_simple_variable_declartion():
    source_file = (
        "DEF Foo()\n"
        "DECL INT bar\n"
        "END"
    )

    awaited_ast = [
        SourceFile(name="Foo", statements=[
            FunctionDefinition(name="Foo", body=[
                VariableSymbol(name="bar", symbol_type="INT")])
        ])]

    parser = Parser()
    parser.add_source_file("Foo", source_file)

    assert awaited_ast == parser.ast


def test_multiple_variable_declartion():
    source_file = (
        "DEF Foo()\n"
        "DECL INT foo\n"
        "DECL INT bar\n"
        "END"
    )

    awaited_ast = [
        SourceFile(name="Foo", statements=[
            FunctionDefinition(name="Foo", body=[
                VariableSymbol(name="foo", symbol_type="INT"),
                VariableSymbol(name="bar", symbol_type="INT")])
        ])]

    parser = Parser()
    parser.add_source_file("Foo", source_file)

    assert awaited_ast == parser.ast


def test_simple_array_declartion():
    source_file = (
        "DEF Foo()\n"
        "DECL INT bar[1]\n"
        "END"
    )

    awaited_ast = [
        SourceFile(name="Foo", statements=[
            FunctionDefinition(name="Foo", body=[
                VariableSymbol(name="bar", symbol_type="INT",
                               dimensions=[1])])
        ])]

    parser = Parser()
    parser.add_source_file("Foo", source_file)

    assert awaited_ast == parser.ast


def test_multi_dimensional_array_declartion():
    source_file = (
        "DEF Foo()\n"
        "DECL INT bar[1, 2, 3]\n"
        "END"
    )

    awaited_ast = [
        SourceFile(name="Foo", statements=[
            FunctionDefinition(name="Foo", body=[
                VariableSymbol(name="bar", symbol_type="INT",
                               dimensions=[1, 2, 3])])
        ])]

    parser = Parser()
    parser.add_source_file("Foo", source_file)

    assert awaited_ast == parser.ast


def test_invalid_multi_dimensional_array_declartion():
    source_file = (
        "DEF Foo()\n"
        "DECL INT bar[1, 2, 3, 4]\n"
        "END"
    )

    parser = Parser()
    with pytest.raises(ParsingError):
        parser.add_source_file("Foo", source_file)


def test_chained_variable_declartion():
    source_file = (
        "DEF Foo()\n"
        "DECL INT bar1, bar2, bar3\n"
        "END"
    )

    awaited_ast = [
        SourceFile(name="Foo", statements=[
            FunctionDefinition(name="Foo", body=[
                VariableSymbol(name="bar1", symbol_type="INT"),
                VariableSymbol(name="bar2", symbol_type="INT"),
                VariableSymbol(name="bar3", symbol_type="INT")
            ])
        ])]

    parser = Parser()
    parser.add_source_file("Foo", source_file)

    assert awaited_ast == parser.ast


def test_chained_array_declartion():
    source_file = (
        "DEF Foo()\n"
        "DECL INT bar1[1, 1], bar2[10]\n"
        "END"
    )

    awaited_ast = [
        SourceFile(name="Foo", statements=[
            FunctionDefinition(name="Foo", body=[
                VariableSymbol(name="bar1", symbol_type="INT",
                               dimensions=[1, 1]),
                VariableSymbol(name="bar2", symbol_type="INT",
                               dimensions=[10])])])]

    parser = Parser()
    parser.add_source_file("Foo", source_file)

    assert awaited_ast == parser.ast


def test_declarations_and_statements():
    source_file = (
        "DEF Foo()\n"
        "DECL INT bar\n"
        "\n"
        "FooBar()"
        "END"
    )

    awaited_ast = [
        SourceFile(name="Foo", statements=[
            FunctionDefinition(name="Foo", body=[
                VariableSymbol(name="bar", symbol_type="INT",
                               dimensions=[0]),
                FunctionCall(name="FooBar")])])]

    parser = Parser()
    parser.add_source_file("Foo", source_file)

    assert awaited_ast == parser.ast
