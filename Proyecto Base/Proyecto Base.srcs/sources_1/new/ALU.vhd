-- REVISAR c en SUB
library IEEE;
use IEEE.STD_LOGIC_1164.ALL;

entity ALU is
    Port ( a        : in  std_logic_vector (15 downto 0);   -- Primer operando.
           b        : in  std_logic_vector (15 downto 0);   -- Segundo operando.
           sop      : in  std_logic_vector (2 downto 0);   -- Selector de la operaci�n.
           c        : out std_logic;                       -- Se�nal de 'carry'.
           z        : out std_logic;                       -- Senal de 'zero'.
           n        : out std_logic;                       -- Senal de 'nagative'.
           result   : out std_logic_vector (15 downto 0));  -- Resultado de la operaci�n.
end ALU;

architecture Behavioral of ALU is

component Adder16
    Port ( a  : in  std_logic_vector (15 downto 0);
           b  : in  std_logic_vector (15 downto 0);
           ci : in  std_logic;
           s  : out std_logic_vector (15 downto 0);
           co : out std_logic);

end component ;

signal add_result   : std_logic_vector(15 downto 0);
signal b_adder   : std_logic_vector(15 downto 0);
signal alu_result   : std_logic_vector(15 downto 0);
signal co_add       : std_logic ;
signal ci_add       : std_logic ;

begin

-- Sumador/Restaror
inst_Adder: Adder16 port map(
        a      => a,
        b      => b_adder,
        ci     => ci_add,
        s      => add_result,
        co     => co_add
    );

with sop select
    b_adder <=  not b    when "001", -- sub 
                b when others;

with sop select
    ci_add <= '1'    when "001", -- sub 
              '0' when others;           
                
-- Resultado de la Operacion
with sop select
    alu_result <= add_result     when "000", -- add
                  add_result     when "001", -- sub
                  a and b     when "010", -- and
                  a or b     when "011", -- or
                  a xor b     when "100", -- xor
                  not a     when "101", -- not
                  '0' & a(15 downto 1)     when "110", -- shr
                  a(14 downto 0) & '0'     when "111"; -- shl
                  
result  <= alu_result;

-- Flags c z n
with sop select
    c <= co_add when "000", -- add
         co_add when "001", -- sub CAMBIO 
         a(0) when "110", -- shr
         a(15) when "111", -- shl
         '0' when others;

with alu_result select         
    z <= '1' when "0000000000000000",
         '0' when others;
    
with sop select 
    n <= not co_add when "001", --sub 
         '0' when others;

end Behavioral;

