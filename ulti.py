S1 = "ÀÁÂÃÈÉÊÌÍÒÓÔÕÙÚÝàáâãèéêìíòóôõùúýĂăĐđĨĩŨũƠơƯưẠạẢảẤấẦầẨẩẪẫẬậẮắẰằẲẳẴẵẶặẸẹẺẻẼẽẾếỀềỂểỄễỆệỈỉỊịỌọỎỏỐốỒồỔổỖỗỘộỚớỜờỞởỠỡỢợỤụỦủỨứỪừỬửỮữỰựỲỳỴỵỶỷỸỹ"
S0 = "AAAAEEEIIOOOOUUYaaaaeeeiioooouuyAaDdIiUuOoUuAaAaAaAaAaAaAaAaAaAaAaAaEeEeEeEeEeEeEeEeIiIiOoOoOoOoOoOoOoOoOoOoOoOoUuUuUuUuUuUuUuYyYyYyYy"
def remove_accents(input_str):
    """Đổi các ký tự từ Uicode sang dạng không dấu và in thường
    Arguments:
        input_str {str} -- string cần chuyển đổi
    Returns:
        str -- string nếu chuyển đổi thành công
        None - otherwise
    """

    if input_str is None:
        return 'none'

    s = ""
    for c in input_str:
        if c in S1:
            s += S0[S1.index(c)]
        else:
            s += c
    return s.lower()





