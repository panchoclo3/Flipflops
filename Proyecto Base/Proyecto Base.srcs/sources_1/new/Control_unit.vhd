library IEEE;
use IEEE.STD_LOGIC_1164.ALL;
-- REVISAR orden de carry, zero y negative en status

entity Control_unit is
    Port ( 
            opcode : in STD_LOGIC_VECTOR(19 downto 0); -- 20 bits de opcode desde la rom
            status : in STD_LOGIC_VECTOR(2 downto 0); --3 bits ordenados: nzc 
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

end Control_unit;

architecture Behavioral of Control_unit is

signal select_jump : STD_LOGIC_VECTOR(3 downto 0);
-- status = 000 -> negative = status(2), zero = status(1), carry = status(0),
signal c : STD_LOGIC;
signal z : STD_LOGIC;
signal n : STD_LOGIC;

begin

-- 20 se�ales de opcode. vector(19 downto 0)
-- la(1), lb(1), w(1), sa(2), sb(2), alu(3), lPC(1), selectJump(3) libres(6)

-- senales para la entrega 1
enableA <= opcode(19);
enableB <= opcode(18);
w <= opcode(17);
selA <= opcode(16 downto 15);
selB <= opcode(14 downto 13);
selALU <= opcode(12 downto 10);

select_jump <= opcode(9 downto 6); --loadPC y los 3 bits siguientes
c <= status(0);
z <= status(1);
n <= status(2);

-- senales para la entrega 2
selAdd <= opcode(5 downto 4);
incSP <= opcode(3);
decSP <= opcode(2);
selPC <= opcode(1);
selDin <= opcode(0);

-- select jump de 4 bits

with select_jump select 
    loadPC <=  '1'   when "1000", -- JMP
               z     when "1001", -- JEQ
               not z  when "1010", -- JNE
               not (n or z)  when "1011", -- JGT
               not n  when "1100", -- JGE
               n    when "1101", -- JLT
               n or z   when "1110", -- JLE
               c    when "1111", -- JCR
              '0'   when others;

end Behavioral;