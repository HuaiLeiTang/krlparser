#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from krlparser.semantic_analyzer import SemanticAnalyzer
from krlparser.symbol_table import SymbolTable
from krlparser.parser import Parser
from krlparser.ast import (FunctionDefinition, Parameter, Module, SourceFile,
                           DataFile, DataDefinition, FunctionSymbol)


def test_simple_module_definition():
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

    global_symbol_table = SymbolTable(name="GLOBAL", parent_scope=None)
    module_symbol_table = SymbolTable(name="Foo",
                                      parent_scope=global_symbol_table)
    function1_symbol_table = SymbolTable(name="Foo.Foo",
                                         parent_scope=module_symbol_table)
    function2_symbol_table = SymbolTable(name="Foo.Bar",
                                         parent_scope=module_symbol_table)

    function_definition1 = FunctionDefinition(
        name="Foo",
        parameters=[Parameter(name="bar",
                              parameter_type=Parameter.TYPE.IN),
                    Parameter(name="foobar",
                              parameter_type=Parameter.TYPE.OUT)],
        is_global=True,
        symbol_table=function1_symbol_table)

    function_definition2 = FunctionDefinition(
        name="Bar", symbol_table=function2_symbol_table)

    awaited_ast = [
        Module(name=module_name,
               source_file=SourceFile(
                   name=module_name,
                   statements=[function_definition1, function_definition2],
                   symbol_table=module_symbol_table),
               data_file=DataFile(
                   name=module_name,
                   statements=[DataDefinition(
                       name="Foo",
                       symbol_table=module_symbol_table)],
                   symbol_table=module_symbol_table))]

    module_symbol_table.add(
        FunctionSymbol.create_from_definition(function_definition1))
    module_symbol_table.add(
        FunctionSymbol.create_from_definition(function_definition2))

    parser = Parser()
    parser.add_module(module_name, source_file, data_file)

    analyzer = SemanticAnalyzer()
    analyzer.visit(parser.ast)

    assert awaited_ast == parser.ast
