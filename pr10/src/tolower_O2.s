	.file	"tolower.c"
	.option pic
	.attribute arch, "rv64i2p1_m2p0_a2p1_f2p2_d2p2_c2p0_zicsr2p0_zifencei2p0"
	.attribute unaligned_access, 0
	.attribute stack_align, 16
	.text
	.align	1
	.globl	my_tolower
	.type	my_tolower, @function
my_tolower:
.LFB23:
	.cfi_startproc
	mv	a3,a1
	li	a6,25
.L5:
	lbu	a5,0(a0)
	addiw	a4,a5,-65
	andi	a4,a4,0xff
	addiw	a2,a5,32
	bgtu	a4,a6,.L2
.L7:
	sb	a2,0(a3)
	lbu	a5,1(a0)
	addi	a3,a3,1
	addi	a0,a0,1
	addiw	a4,a5,-65
	andi	a4,a4,0xff
	addiw	a2,a5,32
	bleu	a4,a6,.L7
.L2:
	sb	a5,0(a3)
	addi	a3,a3,1
	beq	a5,zero,.L4
	addi	a0,a0,1
	j	.L5
.L4:
	subw	a0,a3,a1
	ret
	.cfi_endproc
.LFE23:
	.size	my_tolower, .-my_tolower
	.section	.rodata.str1.8,"aMS",@progbits,1
	.align	3
.LC0:
	.string	"Input:  %s\nOutput: %s\n"
	.section	.text.startup,"ax",@progbits
	.align	1
	.globl	main
	.type	main, @function
main:
.LFB24:
	.cfi_startproc
	addi	sp,sp,-32
	.cfi_def_cfa_offset 32
	sd	s0,16(sp)
	.cfi_offset 8, -16
	lla	s0,.LANCHOR1
	ld	a0,0(s0)
	sd	s1,8(sp)
	.cfi_offset 9, -24
	lla	s1,.LANCHOR0
	mv	a1,s1
	sd	ra,24(sp)
	.cfi_offset 1, -8
	call	my_tolower
	ld	a2,0(s0)
	mv	a3,s1
	lla	a1,.LC0
	li	a0,2
	call	__printf_chk@plt
	ld	ra,24(sp)
	.cfi_restore 1
	ld	s0,16(sp)
	.cfi_restore 8
	ld	s1,8(sp)
	.cfi_restore 9
	li	a0,0
	addi	sp,sp,32
	.cfi_def_cfa_offset 0
	jr	ra
	.cfi_endproc
.LFE24:
	.size	main, .-main
	.globl	outStr
	.globl	tstStr
	.section	.rodata.str1.8
	.align	3
.LC1:
	.string	"Hello World!"
	.bss
	.align	3
	.set	.LANCHOR0,. + 0
	.type	outStr, @object
	.size	outStr, 64
outStr:
	.zero	64
	.section	.data.rel.local,"aw"
	.align	3
	.set	.LANCHOR1,. + 0
	.type	tstStr, @object
	.size	tstStr, 8
tstStr:
	.dword	.LC1
	.ident	"GCC: (Ubuntu 13.3.0-6ubuntu2~24.04.1) 13.3.0"
	.section	.note.GNU-stack,"",@progbits
