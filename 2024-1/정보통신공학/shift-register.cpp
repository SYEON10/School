#include <iostream>
#include <vector>

using namespace std;

const vector<int> CCITT_16 = {1, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1};

//vector<int>를 형식에 맞게 출력하는 함수
void print_vec(const vector<int>& vec){
    for(int i = 0; i < vec.size(); i++){ //벡터를 순회한다.
        cout << ' ' << vec[i]; //형식에 맞게 벡터를 출력한다.
    }
    cout << '\n'; //다음 출력을 위해 enter를 입력한다.
}

//문자열을 vector<int>로 파싱하는 함수
vector<int> parse_string(const string& str){
    vector<int> parsed; //파싱될 vector<int> 생성

    for(int iter = 0, index = 0; iter < str.length(); iter++){ //문자열을 순회하여 parsed 에 저장하는 반복문
        if(str[iter] == ' ') continue; //빈칸일 시 parsed에 저장되지 않는다.
        parsed.push_back(str[iter] - '0'); //char 값을 int 로 parse
        index++; //반복
    }

    return parsed; //파싱된 vector<int>를 반환
}

//shift register 를 계산하는 함수
vector<int> crc_shift_register(vector<int> data, const vector<int>& generator){
    int register_size = int(generator.size() - 1); //shift_register 의 size
    vector<int> shift_register(register_size, 0); //shift_register 로 사용할 벡터
    data.insert(data.end(), shift_register.begin(), shift_register.end()); //원본 데이터에 crc bit 만큼의 0을 추가

    for(int i = 0; i < data.size(); i++){ //데이터를 shift register 에 삽입하는 반복문
        int input = data[i]; //데이터를 data에서 하나씩 빼온다
        int next_input = 0; //shift register 에서 이번 칸의 데이터를 임시로 저장해놓는 변수
        for(int j = register_size - 1; j >= 0; j--){ //shift register 를 순회하는 반복문
            next_input = shift_register[j]; //이번에 저장될 칸의 데이터를 다음 input 으로 사용하기 위해 임시로 저장
            if(generator[j + 1] == 1){ //XOR 계산이 필요할 경우
                shift_register[j] = (input + shift_register.front()) % 2; //XOR 계산 후 shift register 에 저장
            }
            else{//XOR 계산이 필요하지 않을 경우
                shift_register[j] = input; //XOR 계산 없이 shift register 에 저장
            }
            input = next_input; //이번 칸의 데이터를 다음 계산의 input 으로 사용
        }
    }

    return shift_register; //최종 계산된 shift register 를 반환
}

//codeword 를 생성하는 함수
vector<int> create_codeword(vector<int> data, const vector<int>& crc){
    data.insert(data.end(), crc.begin(), crc.end()); //data와 crc bit 를 합친다
    return data; //codeword 를 반환한다.
}

//codeword와 generator 를 보고 error 여부를 확인하는 함수
bool crc_check(const vector<int>& codeword, const vector<int>& generator){
    int crc_start = int(codeword.size() - generator.size() + 1); //crc bit 와 data를 분리하기 위한 기점이다.

    vector<int> data(codeword.begin(), codeword.begin() + crc_start); //codeword 에서 data를 분리한다.
    vector<int> cw_crc(codeword.begin() + crc_start, codeword.end()); //codeword 에서 crc를 분리한다.

    vector<int> crc = crc_shift_register(data, generator); //data로 crc 를 계산한다.

    if(cw_crc == crc){ //data 로부터 계산된 crc와 receive 한 crc가 일치하는지 확인한다.
        return true; //일치할 시 true 를 반환한다.
    }
    return false; //일치하지 않을 시 false 를 반환한다.
}

//TX mode 일 때 실행되는 함수
void TX_mode(const string& data_str, const string& generator_str){
    vector<int> data = parse_string(data_str); //data 를 vector<int>로 파싱한다.
    vector<int> generator = parse_string(generator_str); //generator 를 vector<int>로 파싱한다.

    vector<int> crc_CCITT_16 = crc_shift_register(data, CCITT_16); //CCITT-16으로 crc bit를 계산한다.
    cout << "CRC bits calculated by CCIRR-16: "; //문구 출력
    print_vec(crc_CCITT_16);//CCITT-16으로 계산한 crc bit 를 출력한다.

    vector<int> crc = crc_shift_register(data, generator); //입력받은 generator 로 crc bit를 계산한다.
    cout << "CRC bits calculated by custom generator(" << generator_str << "): "; //문구 출력
    print_vec(crc);//입력받은 generator 로 계산한 crc bit를 출력한다.

    vector<int> codeword_CCITT_16 = create_codeword(data, crc_CCITT_16); //CCITT-16 으로 계산한 crc 비트로 codeword 를 만든다.
    cout << "The complete codeword(CCIRR-16): "; //문구 출력
    print_vec(codeword_CCITT_16); //CCITT-16 codeword 를 출력한다.

    vector<int> codeword = create_codeword(data, crc);//입력받은 generator 로 계산한 crc 비트로 codeword 를 만든다.
    cout << "The complete codeword(custom generator(" << generator_str << ")): "; //문구 출력
    print_vec(codeword);//입력받은 generator codeword 를 출력한다.
}

//RX mode 일 때 실행되는 함수
void RX_mode(const string& codeword_str, const string& generator_str){
    vector<int> codeword = parse_string(codeword_str); //codeword 를 vector<int>로 파싱한다.
    vector<int> generator = parse_string(generator_str); //generator 를 vector<int>로 파싱한다.

    //만약 CCITT-16으로 계산이 불가능한 짧은 codeword가 들어왔을 시 return
    if(generator.size() > codeword.size()){ cout << "Can't Calculate with generator "<< generator_str << '\n';}
    else{
        bool correct = crc_check(codeword, generator); //입력받은 generator 로 correct 여부를 체크한다.

        if(!correct){ //crc bit 가 일치하지 않을 시
            cout << "An error is detected (according to "<<generator_str<<")!"; //에러 문구 출력
        }
        else{ //crc bit 가 일치할 시
            cout << "An error is not detected (according to "<<generator_str<<")!"; //정상 문구 출력
        }
        cout << '\n'; //Enter
    }

    //만약 CCITT-16으로 계산이 불가능한 짧은 codeword가 들어왔을 시 return
    if(CCITT_16.size() > codeword.size()){cout << "Can't Calculate with CCITT-16" << '\n';}
    else{
        bool correct_CCITT_16 = crc_check(codeword, CCITT_16);//CCITT-16으로 correct 여부를 체크한다.

        if(!correct_CCITT_16){//crc bit 가 일치하지 않을 시
            cout << "An error is detected (according to CCITT-16)!"; //에러 문구 출력
        }
        else{//crc bit 가 일치할 시
            cout << "An error is not detected (according to CCITT-16)!"; //정상 문구 출력
        }
        cout << '\n'; //Enter
    }
}

int main() {

    int mode; //입력받을 모드 변수
    string generator_str; //입력받을 generator

    cout << "[HW #3 Part II] Student ID 2171056: SeungYeon Kang" <<'\n'; //문구 출력
    cout << "Select the mode between TX and RX (TX:1, RX:2):"; //문구 출력
    cin >> mode; //mode 입력받기
    cin.ignore(); //getline 입력을 위해 cin 입력에서 enter를 날린다

    if(mode == 1){ //TX 모드일 때
        cout << "Type information bits that you want to send: "; //문구 출력
        string data_str; //데이터를 입력받을 변수
        getline(cin, data_str); //데이터 입력
        cout << "Type generator bits: "; //문구 출력
        getline(cin, generator_str); //generator 입력

        TX_mode(data_str, generator_str); //TX mode 실행

        cout << "Done..."; //문구 출력
    }
    else if(mode == 2){ //RX 모드일 때
        cout << "Type the codeword that RX received:"; //문구 출력
        string codeword_str; //codeword 입력받을 변수
        getline(cin, codeword_str); //codeword 입력
        cout << "Type generator bits: "; //문구 출력
        getline(cin, generator_str); //generator 입력

        RX_mode(codeword_str, generator_str); //RX mode 실행

        cout << "Done..."; //문구 출력
    }
    else cout << "select 1 or 2 again" << '\n'; //예상 입력값 밖일 때 에러 문구 출력

    return 0;
}