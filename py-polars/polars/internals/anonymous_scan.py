from __future__ import annotations

import pickle
from functools import partial
from typing import Any, cast

import polars as pl
from polars import internals as pli
from polars.dependencies import pyarrow as pa  # noqa: TCH001


def _deser_and_exec(  # noqa: D417
    buf: bytes, with_columns: list[str] | None, *args: Any
) -> pli.DataFrame:
    """
    Deserialize and execute the given function for the projected columns.

    Called from polars-lazy. Polars-lazy provides the bytes of the pickled function and
    the projected columns.

    Parameters
    ----------
    buf
        Pickled function
    with_columns
        Columns that are projected

    """
    func = pickle.loads(buf)
    return func(with_columns, *args)


def _scan_pyarrow_dataset_impl(
    ds: pa.dataset.Dataset,
    with_columns: list[str] | None,
    predicate: str | None,
    n_rows: int | None,
) -> pli.DataFrame:
    """
    Take the projected columns and materialize an arrow table.

    Parameters
    ----------
    ds
        pyarrow dataset
    with_columns
        Columns that are projected
    predicate
        pyarrow expression that can be evaluated with eval
    n_rows:
        Materialize only n rows from the arrow dataset

    Returns
    -------
    DataFrame

    """
    _filter = None
    if predicate:
        # imports are used by inline python evaluated by `eval`
        from polars.datatypes import Date, Datetime, Duration  # noqa: F401
        from polars.utils.convert import (
            _to_python_datetime,  # noqa: F401
            _to_python_time,  # noqa: F401
            _to_python_timedelta,  # noqa: F401
        )

        _filter = eval(predicate)
    if n_rows:
        dfs = []
        total_rows = 0
        for rb in ds.to_batches(
            columns=with_columns, filter=_filter, batch_size=n_rows
        ):
            df = pl.DataFrame(dict(zip(rb.schema.names, rb.columns)))
            total_rows += df.height
            dfs.append(df)
            if total_rows > n_rows:
                break
        return pli.concat(dfs, rechunk=False).head(n_rows)

    return cast(
        pli.DataFrame, pl.from_arrow(ds.to_table(columns=with_columns, filter=_filter))
    )


def _scan_pyarrow_dataset(
    ds: pa.dataset.Dataset, allow_pyarrow_filter: bool = True
) -> pli.LazyFrame:
    """
    Pickle the partially applied function `_scan_pyarrow_dataset_impl`.

    The bytes are then sent to the polars logical plan. It can be deserialized once
    executed and ran.

    Parameters
    ----------
    ds
        pyarrow dataset
    allow_pyarrow_filter
        Allow predicates to be pushed down to pyarrow. This can lead to different
        results if comparisons are done with null values as pyarrow handles this
        different than polars does.

    """
    func = partial(_scan_pyarrow_dataset_impl, ds)
    func_serialized = pickle.dumps(func)
    return pli.LazyFrame._scan_python_function(
        ds.schema, func_serialized, allow_pyarrow_filter
    )


def _scan_ipc_impl(  # noqa: D417
    uri: str, with_columns: list[str] | None, *args: Any, **kwargs: Any
) -> pli.DataFrame:
    """
    Take the projected columns and materialize an arrow table.

    Parameters
    ----------
    uri
        Source URI
    with_columns
        Columns that are projected

    """
    import polars as pl

    return pl.read_ipc(uri, with_columns, *args, **kwargs)


def _scan_ipc_fsspec(
    file: str,
    storage_options: dict[str, object] | None = None,
) -> pli.LazyFrame:
    func = partial(_scan_ipc_impl, file, storage_options=storage_options)
    func_serialized = pickle.dumps(func)

    storage_options = storage_options or {}
    with pli._prepare_file_arg(file, **storage_options) as data:
        schema = pli.read_ipc_schema(data)

    return pli.LazyFrame._scan_python_function(schema, func_serialized)


def _scan_parquet_impl(  # noqa: D417
    uri: str, with_columns: list[str] | None, *args: Any, **kwargs: Any
) -> pli.DataFrame:
    """
    Take the projected columns and materialize an arrow table.

    Parameters
    ----------
    uri
        Source URI
    with_columns
        Columns that are projected

    """
    import polars as pl

    return pl.read_parquet(uri, with_columns, *args, **kwargs)


def _scan_parquet_fsspec(
    file: str,
    storage_options: dict[str, object] | None = None,
) -> pli.LazyFrame:
    func = partial(_scan_parquet_impl, file, storage_options=storage_options)
    func_serialized = pickle.dumps(func)

    storage_options = storage_options or {}
    with pli._prepare_file_arg(file, **storage_options) as data:
        schema = pli.read_parquet_schema(data)

    return pli.LazyFrame._scan_python_function(schema, func_serialized)
