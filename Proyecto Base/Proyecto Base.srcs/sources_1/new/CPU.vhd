library IEEE;
use IEEE.STD_LOGIC_1164.ALL;
use IEEE.std_logic_unsigned.all;
use IEEE.numeric_std.all;


entity CPU is
    Port (
           clock : in STD_LOGIC;
           clear : in STD_LOGIC;
           ram_address : out STD_LOGIC_VECTOR (11 downto 0);
           ram_datain : out STD_LOGIC_VECTOR (15 downto 0);
           ram_dataout : in STD_LOGIC_VECTOR (15 downto 0);
           ram_write : out STD_LOGIC;
           rom_address : out STD_LOGIC_VECTOR (11 downto 0);
           rom_dataout : in STD_LOGIC_VECTOR (35 downto 0);
           dis : out STD_LOGIC_VECTOR (15 downto 0);
           status_test : out STD_LOGIC_VECTOR (2 downto 0)); -- ELIMINAR
end CPU;

architecture Behavioral of CPU is

component Reg 
    Port ( clock    : in  std_logic; 
           clear    : in  std_logic;                        
           load     : in  std_logic;                        
           up       : in  std_logic;                        
           down     : in  std_logic;                        
           datain   : in  std_logic_vector (15 downto 0);   
           dataout  : out std_logic_vector (15 downto 0));  
end component;

component ALU
    Port ( a        : in  std_logic_vector (15 downto 0);   
           b        : in  std_logic_vector (15 downto 0);   
           sop      : in  std_logic_vector (2 downto 0);  
           c        : out std_logic;                    
           z        : out std_logic;
           n        : out std_logic;  
           result   : out std_logic_vector (15 downto 0));  
end component;

component Control_unit 
    Port ( 
           opcode : in STD_LOGIC_VECTOR(19 downto 0); -- 36 bits de opcode desde la rom
           status : in STD_LOGIC_VECTOR(2 downto 0); 
           enableA : out STD_LOGIC;
           enableB : out STD_LOGIC;
           selA : out STD_LOGIC_VECTOR(1 downto 0);
           selB : out STD_LOGIC_VECTOR(1 downto 0);
           loadPC : out STD_LOGIC;
           selALU : out STD_LOGIC_VECTOR(2 downto 0);
           w : out STD_LOGIC;
           selAdd : out STD_LOGIC_VECTOR(1 downto 0);
           incSP : out STD_LOGIC;
           decSP : out STD_LOGIC;
           selPC : out STD_LOGIC;
           selDin : out STD_LOGIC
    );

end component;

component PC
    Port ( clock    : in  std_logic;                       
           clear    : in  std_logic;                        
           loadPC     : in  std_logic;                        
           datain   : in  std_logic_vector (11 downto 0);   
           dataout  : out std_logic_vector (11 downto 0));
end component;

component Reg3 
    Port ( clock    : in  std_logic; 
           clear    : in  std_logic;                        
           load     : in  std_logic;                        
           up       : in  std_logic;                        
           down     : in  std_logic;                        
           datain   : in  std_logic_vector (2 downto 0);   
           dataout  : out std_logic_vector (2 downto 0));  
end component;

component SP 
    Port ( clock    : in  std_logic; 
           inc    : in  std_logic;                        
           dec    : in  std_logic;                        
           clear    : in  std_logic;                        
           dataout  : out std_logic_vector (11 downto 0));  
end component;

component Adder12
    Port ( a  : in  std_logic_vector (11 downto 0);
           b  : in  std_logic_vector (11 downto 0);
           ci : in  std_logic;
           s  : out std_logic_vector (11 downto 0);
           co : out std_logic);
end component;

-- Señales de control unit

-- Señales E1
signal enableA : STD_LOGIC;
signal enableB : STD_LOGIC;
signal w : STD_LOGIC;
signal selA : STD_LOGIC_VECTOR(1 downto 0);
signal selB : STD_LOGIC_VECTOR(1 downto 0);
signal selALU : STD_LOGIC_VECTOR(2 downto 0);
signal loadPC : STD_LOGIC;

-- Señales E2
signal selAdd : STD_LOGIC_VECTOR(1 downto 0);
signal incSP : STD_LOGIC;
signal decSP : STD_LOGIC;
signal selPC : STD_LOGIC;
signal selDin : STD_LOGIC;

signal lit : STD_LOGIC_VECTOR(15 downto 0);
signal opcode : STD_LOGIC_VECTOR(19 downto 0);

-- se?ales auxiliares
signal result_alu : STD_LOGIC_VECTOR(15 downto 0);
signal dataout_regA : STD_LOGIC_VECTOR(15 downto 0);
signal dataout_regB : STD_LOGIC_VECTOR(15 downto 0);
signal dataout_muxA : STD_LOGIC_VECTOR(15 downto 0);
signal dataout_muxB : STD_LOGIC_VECTOR(15 downto 0);
signal dataout_status : STD_LOGIC_VECTOR(2 downto 0);
signal alu_flag : STD_LOGIC_VECTOR(2 downto 0);

-- señales E2 auxiliares
signal dout_muxPC : STD_LOGIC_VECTOR(11 downto 0);
signal dout_muxS : STD_LOGIC_VECTOR(11 downto 0);
signal dout_muxDatain : STD_LOGIC_VECTOR(15 downto 0);
signal dout_SP : STD_LOGIC_VECTOR(11 downto 0);
signal hardcode_one : STD_LOGIC_VECTOR(11 downto 0);
signal dout_PC : STD_LOGIC_VECTOR(11 downto 0);
signal dout_Adder : STD_LOGIC_VECTOR(11 downto 0);
signal din_muxDatain : STD_LOGIC_VECTOR(15 downto 0);

begin

lit <= rom_dataout(35 downto 20); --literal son los bit mas significativos
opcode <= rom_dataout(19 downto 0);
ram_datain <= dout_muxDatain; --new
ram_address <= dout_muxS; --new
ram_write <= w;
rom_address <= dout_PC; -- new

status_test <= dataout_status; --NZC. (2)(1)(0). ELIMINAR

dis <= dataout_regA(7 downto 0) & dataout_regB(7 downto 0);

hardcode_one <= "000000000001"; -- new
din_muxDatain <= "0000" & dout_Adder; -- new

-- Unidad de control
inst_Control_unit: Control_unit port map(
    opcode => opcode, -- variable_CU(componente) => variable_CPU
    status => dataout_status,
    enableA => enableA,
    enableB => enableB,
    selA => selA,
    selB => selB,
    loadPC => loadPC,
    selALU => selALU,
    w => w,
    selAdd => selAdd,
    incSP => incSP,
    decSP => decSP,
    selPC => selPC,
    selDin => selDin
);

-- ALU
inst_ALU: ALU port map(
    a => dataout_muxA,
    b => dataout_muxB,
    sop => selALU,
    c => alu_flag(0),
    z => alu_flag(1),
    n => alu_flag(2),
    result => result_alu
);

-- Registros
inst_RegA: Reg port map(
    clock => clock,
    clear => clear,
    load => enableA,
    up => '0',
    down => '0',
    datain => result_alu,
    dataout => dataout_regA
);

inst_RegB: Reg port map(
    clock => clock,
    clear => clear,
    load => enableB,
    up => '0',
    down => '0',
    datain => result_alu,
    dataout => dataout_regB
);

inst_status: Reg3 port map(
    clock => clock,
    clear => clear,
    load => '1', -- load de status es siempre 1 
    up => '0',
    down => '0',
    datain => alu_flag,
    dataout => dataout_status
);

-- Mux A
with selA select
    dataout_muxA <= "0000000000000001" when "01",
                    dataout_regA when "10",
                    "0000000000000000" when others;
        
-- Mux B
with selB select
    dataout_muxB <= ram_dataout when "01",
                    dataout_regB when "10",
                    lit when "11",
                    "0000000000000000" when others;

-- Mux S 
with selAdd select
    dout_muxS <= lit(11 downto 0) when "00",
                 dout_SP when "01",
                 dataout_regB(11 downto 0) when "10",
                 "000000000000" when others; -- ELIMINAR

-- Mux PC
with selPC select
    dout_muxPC <= ram_dataout(11 downto 0) when '1',
                  lit(11 downto 0) when '0';

-- Mux Datain
with selDin select
    dout_muxDatain <= result_alu when '0',
                      din_muxDatain when '1';
    

-- PC
inst_PC: PC port map(
    clock => clock,
    clear => clear,
    loadPC => loadPC,
    datain => dout_muxPC, -- new
    dataout => dout_PC -- new
);


-- Adder
inst_Adder: Adder12 port map(
    a => dout_PC,
    b => hardcode_one,
    ci => '0',
    s => dout_Adder,
    co => open
);

-- SP
inst_SP: SP port map(
    clock => clock,
    inc => incSP,
    dec => decSP,
    clear => clear,
    dataout => dout_SP
);

end Behavioral;