use arrow::array::ListArray;
use polars_arrow::array::ListFromIter;

use super::RepeatBy;
use crate::prelude::*;

type LargeListArray = ListArray<i64>;

impl<T> RepeatBy for ChunkedArray<T>
where
    T: PolarsNumericType,
{
    fn repeat_by(&self, by: &IdxCa) -> ListChunked {
        let iter = self
            .into_iter()
            .zip(by.into_iter())
            .map(|(opt_v, opt_by)| opt_by.map(|by| std::iter::repeat(opt_v).take(by as usize)));

        // Safety:
        // Length of iter is trusted
        unsafe {
            ListChunked::from_chunks(
                self.name(),
                vec![Box::new(LargeListArray::from_iter_primitive_trusted_len::<
                    T::Native,
                    _,
                    _,
                >(iter, T::get_dtype().to_arrow()))],
            )
        }
    }
}
impl RepeatBy for BooleanChunked {
    fn repeat_by(&self, by: &IdxCa) -> ListChunked {
        let iter = self
            .into_iter()
            .zip(by.into_iter())
            .map(|(opt_v, opt_by)| opt_by.map(|by| std::iter::repeat(opt_v).take(by as usize)));

        // Safety:
        // Length of iter is trusted
        unsafe {
            ListChunked::from_chunks(
                self.name(),
                vec![Box::new(LargeListArray::from_iter_bool_trusted_len(iter))],
            )
        }
    }
}
impl RepeatBy for Utf8Chunked {
    fn repeat_by(&self, by: &IdxCa) -> ListChunked {
        // TODO! dispatch via binary.
        if (self.len() != by.len()) & (by.len() == 1) {
            return self.repeat_by(&IdxCa::new(
                "",
                std::iter::repeat(by.get(0).unwrap())
                    .take(self.len())
                    .collect::<Vec<IdxSize>>(),
            ));
        }

        let iter = self
            .into_iter()
            .zip(by.into_iter())
            .map(|(opt_v, opt_by)| opt_by.map(|by| std::iter::repeat(opt_v).take(by as usize)));

        // Safety:
        // Length of iter is trusted
        unsafe {
            ListChunked::from_chunks(
                self.name(),
                vec![Box::new(LargeListArray::from_iter_utf8_trusted_len(
                    iter,
                    self.len(),
                ))],
            )
        }
    }
}
impl RepeatBy for BinaryChunked {
    fn repeat_by(&self, by: &IdxCa) -> ListChunked {
        let iter = self
            .into_iter()
            .zip(by.into_iter())
            .map(|(opt_v, opt_by)| opt_by.map(|by| std::iter::repeat(opt_v).take(by as usize)));

        // Safety:
        // Length of iter is trusted
        unsafe {
            ListChunked::from_chunks(
                self.name(),
                vec![Box::new(LargeListArray::from_iter_binary_trusted_len(
                    iter,
                    self.len(),
                ))],
            )
        }
    }
}
