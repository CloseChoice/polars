initSidebarItems({"enum":[["FromStrError","Reasons why `Utf8Char::from_str()` or `Utf16Char::from_str()` failed."],["InvalidCodepoint","Reasons why an `u32` is not a valid UTF codepoint."],["InvalidUtf16Array","Reasons why a `[u16; 2]` doesn’t form a valid UTF-16 codepoint."],["InvalidUtf16Slice","Reasons why a slice of `u16`s doesn’t start with valid UTF-16."],["InvalidUtf16Tuple","Reasons why one or two `u16`s are not valid UTF-16, in sinking precedence."],["InvalidUtf8","Reasons why a byte sequence is not valid UTF-8, excluding invalid codepoint. In sinking precedence."],["InvalidUtf8Array","Reasons why a byte array is not valid UTF-8, in sinking precedence."],["InvalidUtf8FirstByte","Reasons why a byte is not the start of a UTF-8 codepoint."],["InvalidUtf8Slice","Reasons why a byte slice is not valid UTF-8, in sinking precedence."],["Utf16PairError","Types of invalid sequences encountered by `Utf16CharParser`."]],"struct":[["EmptyStrError","Cannot create an `Utf8Char` or `Utf16Char` from the first codepoint of a str, because there are none."],["InvalidUtf16FirstUnit","Cannot tell whether an `u16` needs an extra unit, because it’s a trailing surrogate itself."]]});